import { DurableObject } from "cloudflare:workers";

export class MyDurableObject extends DurableObject {
	async fetch(request: Request) {
		return new Response("Hello from MyDurableObject");
	}
}
