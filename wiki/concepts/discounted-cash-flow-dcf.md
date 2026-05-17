---
title: Discounted Cash Flow (DCF)
tags: [finance, concepts]
domain: financial-services
last_updated: 2026-05-17
review_status: draft
aliases: []
sources:
  - "LLM synthesis"
related:
  - "Free Cash Flow (FCF)"
  - "Weighted Average Cost of Capital (WACC)"
  - "Gordon Growth Model"
---

# Discounted Cash Flow (DCF)

Discounted Cash Flow (DCF) is a fundamental valuation method used to estimate the value of an investment based on its expected future cash flows, which are discounted back to their present value using a suitable discount rate.

## Key Concepts

- [[Free Cash Flow (FCF)]]: The cash a company generates after accounting for cash outflows to support operations and maintain its capital assets.
- [[Weighted Average Cost of Capital (WACC)]]: The average rate a company is expected to pay to all its security holders to finance its assets, used as the discount rate in DCF models.
- [[Terminal Value]]: The estimated value of a business beyond the explicit forecast period, often calculated using the [[Gordon Growth Model]] or an exit multiple.

## Formula

The basic DCF formula is:

$$DCF = \frac{CF_1}{(1+r)^1} + \frac{CF_2}{(1+r)^2} + \dots + \frac{CF_n}{(1+r)^n} + \frac{TV}{(1+r)^n}$$

Where:
- $CF$: Cash flow for a given period
- $r$: Discount rate (typically [[WACC]])
- $TV$: Terminal Value
- $n$: The number of periods

## Terminal Value Methods

1. **Gordon Growth Model (Perpetuity Growth Method):** Assumes the company will grow at a constant rate forever.
   $$TV = \frac{FCF_{n+1}}{r - g}$$
   *(where $g$ is the perpetual growth rate)*
2. **Exit Multiple Method:** Assumes the company is sold at the end of the forecast period based on a multiple of a metric (e.g., EBITDA).

## Risks & Limitations

- **Sensitivity to Assumptions:** Small changes in the [[WACC]] or terminal growth rate can lead to vastly different valuations.
- **Forecasting Error:** Difficulties in accurately predicting long-term future cash flows.
- **Complexity:** Requires significant data and detailed modeling of business operations.

## See Also
[[Free Cash Flow (FCF)]] | [[Weighted Average Cost of Capital (WACC)]] | [[Gordon Growth Model]]

## Sources
- [Source: LLM synthesis]
