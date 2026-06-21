import { Hono } from "hono";
import { upgradeWebSocket } from "hono/cloudflare-workers";
import { MyDurableObject } from "./my-durable-object";

const app = new Hono();

app.get("/server-health", (c) => {
    return c.json(
        {
            status: "ok",
            timestamp: new Date().toISOString(),
            version: "1.0.0"
            
        }
    )
})




export default app;

export { MyDurableObject };
