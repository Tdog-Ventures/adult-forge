-- Seed minimal User + CreatorProfile so Video.creatorId FK succeeds
INSERT INTO "User" (id, email, username, role, "createdAt")
VALUES (
  'seed-user-test1',
  'seed-test1@local.invalid',
  'seed_test1_user',
  'SUBSCRIBER'::"Role",
  NOW()
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO "CreatorProfile" (id, "userId", "displayName")
VALUES ('seed-cp-test1', 'seed-user-test1', 'Seed Creator')
ON CONFLICT (id) DO NOTHING;

INSERT INTO "Video" (id, title, "creatorId", status, "hlsMasterUrl", "thumbnailUrl", "createdAt")
VALUES (
  'test1',
  'Demo',
  'seed-cp-test1',
  'READY',
  'https://cdn.test/video.m3u8',
  'https://cdn.test/thumb.jpg',
  NOW()
)
ON CONFLICT (id) DO UPDATE SET
  status = 'READY',
  "hlsMasterUrl" = 'https://cdn.test/video.m3u8';
