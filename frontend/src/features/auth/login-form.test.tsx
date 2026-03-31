import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { AppProviders } from "../../app/providers";
import { LoginForm } from "./login-form";

describe("LoginForm", () => {
  it("shows validation messages when submitted empty", async () => {
    render(
      <MemoryRouter>
        <AppProviders>
          <LoginForm />
        </AppProviders>
      </MemoryRouter>,
    );

    fireEvent.click(screen.getByRole("button", { name: "Увійти" }));

    expect(await screen.findByText("Вкажіть коректний email.")).toBeInTheDocument();
    expect(await screen.findByText("Пароль має містити щонайменше 8 символів.")).toBeInTheDocument();
  });
});
