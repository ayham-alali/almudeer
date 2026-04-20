import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

export interface SyncPayload {
  tasks?: { created?: any[]; updated?: any[]; deleted?: string[] };
  notes?: { created?: any[]; updated?: any[]; deleted?: string[] };
  customers?: { created?: any[]; updated?: any[]; deleted?: string[] };
}

@Injectable()
export class SyncService {
  constructor(private readonly prisma: PrismaService) {}

  async pushSync(userId: string, payload: SyncPayload) {
    const { tasks, notes, customers } = payload;

    // Run sync operations inside a Prisma Transaction for atomic data integrity
    await this.prisma.$transaction(async (tx) => {
      // --- 1. TASKS SYNC ---
      if (tasks) {
        const upsertTasks = [...(tasks.created || []), ...(tasks.updated || [])];
        for (const task of upsertTasks) {
          const { id, ...data } = task;
          await tx.task.upsert({
            where: { id: id },
            create: { ...data, id, ownerId: userId },
            update: { ...data, ownerId: userId },
          });
        }
        if (tasks.deleted && tasks.deleted.length > 0) {
          await tx.task.updateMany({
            where: { id: { in: tasks.deleted }, ownerId: userId },
            data: { deletedAt: new Date() },
          });
        }
      }

      // --- 2. NOTES SYNC ---
      if (notes) {
        const upsertNotes = [...(notes.created || []), ...(notes.updated || [])];
        for (const note of upsertNotes) {
          const { id, ...data } = note;
          await tx.note.upsert({
            where: { id: id },
            create: { ...data, id, ownerId: userId },
            update: { ...data, ownerId: userId },
          });
        }
        if (notes.deleted && notes.deleted.length > 0) {
          await tx.note.updateMany({
            where: { id: { in: notes.deleted }, ownerId: userId },
            data: { deletedAt: new Date() },
          });
        }
      }

      // --- 3. CUSTOMERS SYNC ---
      if (customers) {
        const upsertCustomers = [...(customers.created || []), ...(customers.updated || [])];
        for (const customer of upsertCustomers) {
          const { id, ...data } = customer;
          await tx.customer.upsert({
            where: { id: id },
            create: { ...data, id, ownerId: userId },
            update: { ...data, ownerId: userId },
          });
        }
        if (customers.deleted && customers.deleted.length > 0) {
          await tx.customer.updateMany({
            where: { id: { in: customers.deleted }, ownerId: userId },
            data: { deletedAt: new Date() },
          });
        }
      }
    });

    return {
      success: true,
      message: 'Sync completed successfully',
      timestamp: new Date().toISOString(),
    };
  }
}
