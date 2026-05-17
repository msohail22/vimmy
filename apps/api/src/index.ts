import { Hono } from "hono";
import { upgradeWebSocket } from "hono/cloudflare-workers";
import { MyDurableObject } from "./my-durable-object";

const app = new Hono();


app.get("/", (c) => c.text("Hono!"));

export default app;

export { MyDurableObject };
