-- Migration: Initial schema from Django to Prisma
-- Created: 2026-04-20

-- Drop old Django/alembic tables (they contain data but are no longer needed)
DROP TABLE IF EXISTS alembic_version CASCADE;
DROP TABLE IF EXISTS app_config CASCADE;
DROP TABLE IF EXISTS customer_presence CASCADE;
DROP TABLE IF EXISTS system_locks CASCADE;
DROP TABLE IF EXISTS telegram_entities CASCADE;
DROP TABLE IF EXISTS update_events CASCADE;
DROP TABLE IF EXISTS user_accounts CASCADE;
DROP TABLE IF EXISTS version_history CASCADE;

-- Create new Prisma schema tables

-- Create enum types
DO $$ BEGIN
    CREATE TYPE "UserStatus" AS ENUM ('PENDING', 'ACTIVE', 'EXPIRED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE "TaskPriority" AS ENUM ('HIGH', 'MEDIUM', 'LOW');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE "TaskStatus" AS ENUM ('TODO', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE "RecurringType" AS ENUM ('NONE', 'DAILY', 'WEEKLY', 'MONTHLY');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE "LedgerTransactionType" AS ENUM ('DEBT_FOR_ME', 'DEBT_ON_ME', 'PAYMENT_RECEIVED', 'PAYMENT_SENT');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE "ResourceType" AS ENUM ('TASK', 'NOTE', 'CUSTOMER');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE "PermissionLevel" AS ENUM ('VIEW', 'EDIT', 'TRANSFER_OWNERSHIP');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE "SystemTaskType" AS ENUM ('ADHKAR', 'QURAN');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create User table
CREATE TABLE "User" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "fullName" TEXT NOT NULL,
    "username" TEXT NOT NULL UNIQUE,
    "email" TEXT NOT NULL UNIQUE,
    "passwordHash" TEXT NOT NULL,
    "avatarUrl" TEXT,
    "status" "UserStatus" NOT NULL DEFAULT 'PENDING',
    "trialEndsAt" TIMESTAMP,
    "followersCount" INTEGER NOT NULL DEFAULT 0,
    "followingCount" INTEGER NOT NULL DEFAULT 0,
    "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "deletedAt" TIMESTAMP
);

-- Create Task table
CREATE TABLE "Task" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "title" TEXT NOT NULL,
    "description" TEXT,
    "ownerId" UUID NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
    "priority" "TaskPriority" NOT NULL DEFAULT 'MEDIUM',
    "status" "TaskStatus" NOT NULL DEFAULT 'TODO',
    "dueDate" TIMESTAMP,
    "isRecurring" "RecurringType" NOT NULL DEFAULT 'NONE',
    "alarmEnabled" BOOLEAN NOT NULL DEFAULT false,
    "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "deletedAt" TIMESTAMP
);

-- Create Note table
CREATE TABLE "Note" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "title" TEXT NOT NULL,
    "content" TEXT,
    "ownerId" UUID NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
    "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "deletedAt" TIMESTAMP
);

-- Create Customer table
CREATE TABLE "Customer" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "name" TEXT NOT NULL,
    "phone" TEXT,
    "description" TEXT,
    "ownerId" UUID NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
    "totalDebtForMe" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "totalDebtOnMe" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "currency" TEXT NOT NULL DEFAULT 'USD',
    "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "deletedAt" TIMESTAMP
);

-- Create LedgerTransaction table
CREATE TABLE "LedgerTransaction" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "customerId" UUID NOT NULL REFERENCES "Customer"("id") ON DELETE CASCADE,
    "amount" DOUBLE PRECISION NOT NULL,
    "type" "LedgerTransactionType" NOT NULL,
    "date" TIMESTAMP NOT NULL DEFAULT NOW(),
    "notes" TEXT,
    "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "deletedAt" TIMESTAMP
);

-- Create SharedResource table
CREATE TABLE "SharedResource" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "resourceType" "ResourceType" NOT NULL,
    "resourceId" UUID NOT NULL,
    "ownerId" UUID NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
    "sharedWithUserId" UUID NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
    "permissionLevel" "PermissionLevel" NOT NULL DEFAULT 'VIEW',
    "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "deletedAt" TIMESTAMP,
    CONSTRAINT "SharedResource_ownerId_fkey" FOREIGN KEY ("ownerId") REFERENCES "User"("id") ON DELETE CASCADE,
    CONSTRAINT "SharedResource_sharedWithUserId_fkey" FOREIGN KEY ("sharedWithUserId") REFERENCES "User"("id") ON DELETE CASCADE
);

-- Create SystemTaskLog table
CREATE TABLE "SystemTaskLog" (
    "id" UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "userId" UUID NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
    "taskType" "SystemTaskType" NOT NULL,
    "completedAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "createdAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "updatedAt" TIMESTAMP NOT NULL DEFAULT NOW(),
    "deletedAt" TIMESTAMP
);

-- Create indexes
CREATE INDEX "Task_ownerId_idx" ON "Task"("ownerId");
CREATE INDEX "Note_ownerId_idx" ON "Note"("ownerId");
CREATE INDEX "Customer_ownerId_idx" ON "Customer"("ownerId");
CREATE INDEX "LedgerTransaction_customerId_idx" ON "LedgerTransaction"("customerId");
CREATE INDEX "SystemTaskLog_userId_idx" ON "SystemTaskLog"("userId");
CREATE INDEX "SharedResource_ownerId_idx" ON "SharedResource"("ownerId");
CREATE INDEX "SharedResource_sharedWithUserId_idx" ON "SharedResource"("sharedWithUserId");
