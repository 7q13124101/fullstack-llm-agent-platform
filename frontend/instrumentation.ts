import { registerOTel } from "@vercel/otel";

export function register() {
  registerOTel({
    serviceName: "fullstack_llm_agent_platform-frontend",
  });
}