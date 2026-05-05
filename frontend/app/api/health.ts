export type HealthResponse = {
  status: "ok";
  service: "frontend";
};

export function getHealth(): HealthResponse {
  return { status: "ok", service: "frontend" };
}
