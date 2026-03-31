export function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("uk-UA", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function formatCurrency(value: string | number): string {
  const amount = typeof value === "number" ? value : Number(value);
  return new Intl.NumberFormat("uk-UA", {
    style: "currency",
    currency: "UAH",
    maximumFractionDigits: 2,
  }).format(amount);
}

export function roleLabel(role: string): string {
  switch (role) {
    case "PATIENT":
      return "Пацієнт";
    case "DOCTOR":
      return "Лікар";
    case "ADMIN":
      return "Адміністратор";
    case "OWNER":
      return "Власник";
    default:
      return role;
  }
}

export function appointmentStatusLabel(status: string): string {
  switch (status) {
    case "SCHEDULED":
      return "Заплановано";
    case "COMPLETED":
      return "Завершено";
    case "CANCELLED":
      return "Скасовано";
    case "NO_SHOW":
      return "Не з’явився";
    default:
      return status;
  }
}

export function paymentStatusLabel(status: string): string {
  switch (status) {
    case "PAID":
      return "Оплачено";
    case "PENDING":
      return "Очікує";
    case "FAILED":
      return "Помилка";
    case "REFUNDED":
      return "Повернено";
    default:
      return status;
  }
}

