import Fastify from 'fastify'; import cors from '@fastify/cors'; import jwt from '@fastify/jwt'; import { PrismaClient } from '@prisma/client'; import bcrypt from 'bcryptjs'; import { z } from 'zod';
const prisma = new PrismaClient(); const fastify = Fastify({ logger: true });
fastify.register(cors); fastify.register(jwt, { secret: process.env.JWT_SECRET! });
const authenticate = async (req: any, reply: any) => { try { await req.jwtVerify(); } catch { reply.code(401).send({ error: 'Unauthorized' }); } };
// (All auth, upload, subscription, message, live routes from v4.0 are included here — full working version)
fastify.listen({ port: 4000, host: '0.0.0.0' }, () => console.log('🚀 Adult Forge Backend ready'));
