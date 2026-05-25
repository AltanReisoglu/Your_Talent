import { StatusBanner } from "./StatusBanner";

export function FinancialSafetyNotice() {
  return (
    <StatusBanner
      tone="warning"
      title="Financial education only"
      message="FinWiki provides research and education. It does not provide personalized investment, trading, lending, brokerage, crypto custody, or money-management advice."
    />
  );
}
