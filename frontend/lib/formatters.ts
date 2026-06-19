const inrFormatter = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  minimumFractionDigits: 0,
  maximumFractionDigits: 0,
});

export function formatCurrencyInr(amount: number) {
  return inrFormatter.format(amount).replace(/\s+/g, "");
}
