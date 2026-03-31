const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function normalizeEmail(email: string): string {
  return email.trim().toLowerCase();
}

export function getEmailValidationError(email: string): string | null {
  const normalized = normalizeEmail(email);

  if (!normalized) {
    return "Please enter your email address.";
  }

  if (!EMAIL_REGEX.test(normalized)) {
    return "Please enter a valid email address.";
  }

  return null;
}

export function getDisplayNameValidationError(name: string): string | null {
  const trimmed = name.trim();

  if (!trimmed) {
    return "Please enter your name.";
  }

  if (trimmed.length < 2) {
    return "Name must be at least 2 characters.";
  }

  return null;
}

export function getPasswordValidationError(password: string): string | null {
  if (!password) {
    return "Please enter your password.";
  }

  if (password.length < 6) {
    return "Password must be at least 6 characters.";
  }

  return null;
}
