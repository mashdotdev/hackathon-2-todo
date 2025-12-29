/**
 * Health check endpoint for Kubernetes liveness probe.
 * Returns OK if Next.js server is running.
 */
import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({ status: "ok" });
}
