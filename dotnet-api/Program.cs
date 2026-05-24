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

app.Run(Environment.GetEnvironmentVariable("FINWIKI_DOTNET_URL") ?? "http://0.0.0.0:8000");

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
