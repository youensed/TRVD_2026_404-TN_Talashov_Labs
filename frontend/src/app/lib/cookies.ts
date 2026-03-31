export function readCookie(name: string): string | null {
  const cookies = document.cookie.split(";").map((item) => item.trim());
  const entry = cookies.find((item) => item.startsWith(`${name}=`));
  if (!entry) {
    return null;
  }
  return decodeURIComponent(entry.slice(name.length + 1));
}

