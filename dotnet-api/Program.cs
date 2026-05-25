using System.Diagnostics;
using System.Text.Json;
using System.Text.Json.Serialization;

var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();
var jsonOptions = new JsonSerializerOptions
{
    PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
    WriteIndented = false
};

app.UseDefaultFiles();
app.UseStaticFiles();

app.MapGet("/health", () => Results.Ok(new
{
    status = "ok",
    service = "finwiki-dotnet-api"
}));

app.MapPost("/invoke", async (InvokeRequest request) =>
{
    if (string.IsNullOrWhiteSpace(request.Message))
    {
        return Results.BadRequest(new { detail = "message is required" });
    }

    var repoRoot = FindRepoRoot();
    var pythonPath = ResolvePythonPath(repoRoot);
    var payload = JsonSerializer.Serialize(request, jsonOptions);

    var startInfo = new ProcessStartInfo
    {
        FileName = pythonPath,
        Arguments = "scripts/invoke_agent.py",
        WorkingDirectory = repoRoot,
        RedirectStandardInput = true,
        RedirectStandardOutput = true,
        RedirectStandardError = true,
        UseShellExecute = false
    };

    startInfo.Environment["PYTHONUNBUFFERED"] = "1";

    using var process = Process.Start(startInfo);
    if (process is null)
    {
        return Results.Problem("Failed to start Python FinWiki worker.");
    }

    await process.StandardInput.WriteAsync(payload);
    process.StandardInput.Close();

    var stdoutTask = process.StandardOutput.ReadToEndAsync();
    var stderrTask = process.StandardError.ReadToEndAsync();

    await process.WaitForExitAsync();

    var stdout = await stdoutTask;
    var stderr = await stderrTask;

    if (process.ExitCode != 0)
    {
        return Results.Problem(
            detail: Redact(stderr),
            title: "Python FinWiki worker failed",
            statusCode: 502
        );
    }

    try
    {
        var response = JsonSerializer.Deserialize<InvokeResponse>(stdout, jsonOptions);
        return response is null
            ? Results.Problem("Python worker returned an empty response.", statusCode: 502)
            : Results.Ok(response);
    }
    catch (JsonException)
    {
        return Results.Problem(
            detail: Redact(stdout),
            title: "Python worker returned invalid JSON",
            statusCode: 502
        );
    }
});

app.MapGet("/wiki/search", async (string q, string? category, int? limit) =>
{
    if (string.IsNullOrWhiteSpace(q))
    {
        return Results.BadRequest(new
        {
            error = new
            {
                code = "query_required",
                message = "q is required.",
                retryable = false
            }
        });
    }

    return await RunPythonJsonScript("scripts/wiki_api.py", new
    {
        operation = "search",
        query = q,
        category,
        limit = limit ?? 10
    }, jsonOptions);
});

app.MapGet("/wiki/page", async (string path) =>
{
    if (string.IsNullOrWhiteSpace(path))
    {
        return Results.BadRequest(new
        {
            error = new
            {
                code = "path_required",
                message = "path is required.",
                retryable = false
            }
        });
    }

    return await RunPythonJsonScript("scripts/wiki_api.py", new
    {
        operation = "page",
        path
    }, jsonOptions);
});

app.MapPost("/ingest-submissions", async (IngestSubmissionRequest request) =>
{
    return await RunPythonJsonScript("scripts/wiki_api.py", new
    {
        operation = "ingest_submission",
        request.UserId,
        request.Type,
        request.Content,
        request.Notes
    }, jsonOptions);
});

app.MapPost("/account/delete", async (AccountDeleteRequest request) =>
{
    return await RunPythonJsonScript("scripts/wiki_api.py", new
    {
        operation = "account_delete",
        request.UserId,
        request.Confirmation
    }, jsonOptions);
});

app.Run(Environment.GetEnvironmentVariable("FINWIKI_DOTNET_URL") ?? "http://0.0.0.0:8000");

static async Task<IResult> RunPythonJsonScript(
    string scriptPath,
    object payload,
    JsonSerializerOptions jsonOptions
)
{
    var repoRoot = FindRepoRoot();
    var pythonPath = ResolvePythonPath(repoRoot);
    var serializedPayload = JsonSerializer.Serialize(payload, jsonOptions);

    var startInfo = new ProcessStartInfo
    {
        FileName = pythonPath,
        Arguments = scriptPath,
        WorkingDirectory = repoRoot,
        RedirectStandardInput = true,
        RedirectStandardOutput = true,
        RedirectStandardError = true,
        UseShellExecute = false
    };

    startInfo.Environment["PYTHONUNBUFFERED"] = "1";

    using var process = Process.Start(startInfo);
    if (process is null)
    {
        return Results.Problem("Failed to start Python FinWiki worker.");
    }

    await process.StandardInput.WriteAsync(serializedPayload);
    process.StandardInput.Close();

    var stdoutTask = process.StandardOutput.ReadToEndAsync();
    var stderrTask = process.StandardError.ReadToEndAsync();

    await process.WaitForExitAsync();

    var stdout = await stdoutTask;
    var stderr = await stderrTask;

    if (process.ExitCode != 0)
    {
        return Results.Problem(
            detail: Redact(stderr),
            title: "Python FinWiki worker failed",
            statusCode: 502
        );
    }

    try
    {
        var response = JsonSerializer.Deserialize<JsonElement>(stdout, jsonOptions);
        if (response.ValueKind == JsonValueKind.Object &&
            response.TryGetProperty("error", out var error) &&
            error.ValueKind == JsonValueKind.Object)
        {
            var statusCode = 400;
            if (error.TryGetProperty("code", out var code) &&
                code.ValueKind == JsonValueKind.String &&
                code.GetString() == "wiki_page_not_found")
            {
                statusCode = 404;
            }

            return Results.Json(response, jsonOptions, statusCode: statusCode);
        }

        return Results.Json(response, jsonOptions);
    }
    catch (JsonException)
    {
        return Results.Problem(
            detail: Redact(stdout),
            title: "Python worker returned invalid JSON",
            statusCode: 502
        );
    }
}

static string FindRepoRoot()
{
    var current = new DirectoryInfo(AppContext.BaseDirectory);
    while (current is not null)
    {
        if (File.Exists(Path.Combine(current.FullName, "pyproject.toml")) &&
            Directory.Exists(Path.Combine(current.FullName, "agents")))
        {
            return current.FullName;
        }
        current = current.Parent;
    }

    return Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "../../.."));
}

static string ResolvePythonPath(string repoRoot)
{
    var venvPython = Path.Combine(repoRoot, ".venv", "bin", "python");
    return File.Exists(venvPython) ? venvPython : "python3";
}

static string Redact(string text)
{
    foreach (var key in new[] { "GOOGLE_API_KEY", "TAVILY_API_KEY", "HF_TOKEN", "HUGGINGFACEHUB_API_TOKEN", "LANGSMITH_API_KEY" })
    {
        var value = Environment.GetEnvironmentVariable(key);
        if (!string.IsNullOrWhiteSpace(value))
        {
            text = text.Replace(value, "[redacted]");
        }
    }

    return text;
}

record InvokeRequest(
    [property: JsonPropertyName("user_id")] string UserId,
    [property: JsonPropertyName("session_id")] string SessionId,
    [property: JsonPropertyName("message")] string Message
);

record InvokeResponse(
    [property: JsonPropertyName("user_id")] string UserId,
    [property: JsonPropertyName("session_id")] string SessionId,
    [property: JsonPropertyName("thread_id")] string ThreadId,
    [property: JsonPropertyName("response")] string Response,
    [property: JsonPropertyName("hooks")] JsonElement? Hooks
);

record IngestSubmissionRequest(
    [property: JsonPropertyName("user_id")] string UserId,
    [property: JsonPropertyName("type")] string Type,
    [property: JsonPropertyName("content")] string Content,
    [property: JsonPropertyName("notes")] string? Notes
);

record AccountDeleteRequest(
    [property: JsonPropertyName("user_id")] string UserId,
    [property: JsonPropertyName("confirmation")] bool Confirmation
);
