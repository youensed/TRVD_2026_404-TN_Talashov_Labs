import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { z } from "zod";

import { api } from "../../app/lib/api";
import { useSessionStore } from "../../app/store/session-store";

const schema = z.object({
  email: z.string().email("Вкажіть коректний email."),
  password: z.string().min(8, "Пароль має містити щонайменше 8 символів."),
});

type FormValues = z.infer<typeof schema>;

export function LoginForm() {
  const navigate = useNavigate();
  const setViewer = useSessionStore((state) => state.setViewer);

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const mutation = useMutation({
    mutationFn: api.auth.login,
    onSuccess: (data) => {
      setViewer(data.user);
      void navigate("/app");
    },
  });

  const handleSubmit = form.handleSubmit((values) => mutation.mutate(values));

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      <div>
        <label className="mb-2 block text-sm font-semibold text-slate-700" htmlFor="login-email">
          Email
        </label>
        <input className="field" id="login-email" type="email" {...form.register("email")} />
        <p className="mt-2 text-sm text-rose-600">{form.formState.errors.email?.message}</p>
      </div>

      <div>
        <label className="mb-2 block text-sm font-semibold text-slate-700" htmlFor="login-password">
          Пароль
        </label>
        <input className="field" id="login-password" type="password" {...form.register("password")} />
        <p className="mt-2 text-sm text-rose-600">{form.formState.errors.password?.message}</p>
      </div>

      {mutation.error ? <p className="text-sm text-rose-600">{mutation.error.message}</p> : null}

      <button className="btn-primary w-full" disabled={mutation.isPending} type="submit">
        {mutation.isPending ? "Входимо..." : "Увійти"}
      </button>
    </form>
  );
}

