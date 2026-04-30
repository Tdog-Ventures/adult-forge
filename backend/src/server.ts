import "dotenv/config";
import Fastify from "fastify";
import cors from "@fastify/cors";
import jwt from "@fastify/jwt";
import { PrismaClient } from "@prisma/client";
import { z } from "zod";

const prisma = new PrismaClient();
const fastify = Fastify({ logger: true });

fastify.register(cors, { origin: true });
fastify.register(jwt, { secret: process.env.JWT_SECRET! });

const BatchStatusSchema = z.object({
  job_ids: z.array(z.string()).min(1).max(100),
});

fastify.post("/api/external/render-video-status", async (req, reply) => {
  const auth = req.headers.authorization;
  const apiKey = process.env.FACELESSFORGE_API_KEY;

  if (!auth?.startsWith("Bearer ") || !apiKey || auth.slice(7) !== apiKey) {
    return reply.code(401).send({ error: "Invalid API key" });
  }

  const parsed = BatchStatusSchema.safeParse(req.body);
  if (!parsed.success) {
    return reply
      .code(400)
      .send({ error: "Invalid request", details: parsed.error.flatten() });
  }

  const { job_ids } = parsed.data;
  const videos = await prisma.video.findMany({
    where: { id: { in: job_ids } },
    select: { id: true, status: true, hlsMasterUrl: true, thumbnailUrl: true },
  });

  const videoMap = new Map(videos.map((v) => [v.id, v]));

  const results = job_ids.map((id) => {
    const v = videoMap.get(id);
    if (!v) return { job_id: id, status: "pending" };

    const status =
      v.status === "READY" || v.hlsMasterUrl
        ? "completed"
        : v.status === "FAILED"
          ? "failed"
          : "pending";

    return {
      job_id: id,
      status,
      video_url: v.hlsMasterUrl || undefined,
      thumbnail_url: v.thumbnailUrl || undefined,
    };
  });

  return {
    completed: results.filter((r) => r.status === "completed").length,
    failed: results.filter((r) => r.status === "failed").length,
    pending: results.filter((r) => r.status === "pending").length,
    videos: results,
  };
});

fastify.listen({ port: 4000, host: "0.0.0.0" }, (err) => {
  if (err) throw err;
  console.log("🚀 Adult Forge Backend ready on http://localhost:4000");
});
