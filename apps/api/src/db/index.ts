import { drizzle } from "drizzle-orm/d1";


export const getDB = (db: D1Database) => {
	return drizzle(db);
};
