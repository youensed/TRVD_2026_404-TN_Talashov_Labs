import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { z } from "zod";

import { api } from "../../app/lib/api";
import { useSessionStore } from "../../app/store/session-store";

const schema = z.object({
  first_name: z.string().min(2, "Вкажіть ім’я."),
  last_name: z.string().min(2, "Вкажіть прізвище."),
  email: z.string().email("Вкажіть коректний email."),
  phone: z.string().optional(),
  password: z.string().min(8, "Пароль має містити щонайменше 8 символів."),
});

type FormValues = z.infer<typeof schema>;

export function RegisterForm() {
  const navigate = useNavigate();
  const setViewer = useSessionStore((state) => state.setViewer);

  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      first_name: "",
      last_name: "",
      email: "",
      phone: "",
      password: "",
    },
  });

  const mutation = useMutation({
    mutationFn: api.auth.register,
    onSuccess: (data) => {
      setViewer(data.user);
      void navigate("/app");
    },
  });

  const handleSubmit = form.handleSubmit((values) => mutation.mutate(values));

  return (
    <form className="space-y-4" onSubmit={handleSubmit}>
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-2 block text-sm font-semibold text-slate-700">Ім’я</label>
          <input className="field" type="text" {...form.register("first_name")} />
          <p className="mt-2 text-sm text-rose-600">{form.formState.errors.first_name?.message}</p>
        </div>
        <div>
          <label className="mb-2 block text-sm font-semibold text-slate-700">Прізвище</label>
          <input className="field" type="text" {...form.register("last_name")} />
          <p className="mt-2 text-sm text-rose-600">{form.formState.errors.last_name?.message}</p>
        </div>
      </div>

      <div>
        <label className="mb-2 block text-sm font-semibold text-slate-700">Email</label>
        <input className="field" type="email" {...form.register("email")} />
        <p className="mt-2 text-sm text-rose-600">{form.formState.errors.email?.message}</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-2 block text-sm font-semibold text-slate-700">Телефон</label>
          <input className="field" type="text" {...form.register("phone")} />
        </div>
        <div>
          <label className="mb-2 block text-sm font-semibold text-slate-700">Пароль</label>
          <input className="field" type="password" {...form.register("password")} />
          <p className="mt-2 text-sm text-rose-600">{form.formState.errors.password?.message}</p>
        </div>
      </div>

      {mutation.error ? <p className="text-sm text-rose-600">{mutation.error.message}</p> : null}

      <button className="btn-primary w-full" disabled={mutation.isPending} type="submit">
        {mutation.isPending ? "Створюємо профіль..." : "Створити обліковий запис"}
      </button>
    </form>
  );
}

