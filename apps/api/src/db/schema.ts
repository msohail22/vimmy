import { sqliteTable, integer, text } from "drizzle-orm/sqlite-core";

export const users = sqliteTable("users", {
	id: integer("id").primaryKey({ autoIncrement: true }),
	username: text("username").notNull().unique(),
	createdAt: integer("created_at", { mode: "timestamp" }).notNull(),
});
