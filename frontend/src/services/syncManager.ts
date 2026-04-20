import { db } from '../db/db';
import { api } from './api';

const groupItems = (items: any[]) => ({
  created: items.filter(item => item.syncStatus === 'CREATED'),
  updated: items.filter(item => item.syncStatus === 'UPDATED'),
  deleted: items.filter(item => item.syncStatus === 'DELETED'),
});

export const pushOfflineChanges = async () => {
  if (!navigator.onLine) return; // Exit if still offline

  console.log('[Sync Manager] Starting offline data sync...');

  try {
    // 1. Fetch all unsynced data
    const unsyncedTasks = await db.tasks.filter(t => t.syncStatus !== 'SYNCED').toArray();
    const unsyncedNotes = await db.notes.filter(n => n.syncStatus !== 'SYNCED').toArray();
    const unsyncedCustomers = await db.customers.filter(c => c.syncStatus !== 'SYNCED').toArray();
    const unsyncedLedger = await db.ledger.filter(l => l.syncStatus !== 'SYNCED').toArray();

    // Prevent unnecessary network request if nothing to sync
    if (!unsyncedTasks.length && !unsyncedNotes.length && !unsyncedCustomers.length && !unsyncedLedger.length) {
      console.log('[Sync Manager] No offline changes pending.');
      return;
    }

    // 2. Group data by entity and syncStatus (CREATED, UPDATED, DELETED)
    const payload = {
      tasks: groupItems(unsyncedTasks),
      notes: groupItems(unsyncedNotes),
      customers: groupItems(unsyncedCustomers),
      ledger: groupItems(unsyncedLedger)
    };

    // 3. Send grouped payload via single POST request
    const response = await api.post('/sync/push', payload);

    if (response.status === 200 || response.status === 201) {
      // 4. On success, mark as SYNCED locally or remove from DB if DELETED
      
      const processLocalSuccess = async (table: any, items: any[]) => {
        for (const item of items) {
          if (item.syncStatus === 'DELETED') {
            await table.delete(item.id);
          } else {
            await table.update(item.id, { syncStatus: 'SYNCED' });
          }
        }
      };

      await processLocalSuccess(db.tasks, unsyncedTasks);
      await processLocalSuccess(db.notes, unsyncedNotes);
      await processLocalSuccess(db.customers, unsyncedCustomers);
      await processLocalSuccess(db.ledger, unsyncedLedger);

      console.log('[Sync Manager] Data successfully synced with backend!');
    }
  } catch (error) {
    console.error('[Sync Manager] Critical sync failure', error);
  }
};

export const initializeSyncManager = () => {
  if (typeof window !== 'undefined') {
    // Sync when coming online
    window.addEventListener('online', pushOfflineChanges);
    
    // Also try syncing periodically or right now if it's already online at startup
    if (navigator.onLine) {
      setTimeout(pushOfflineChanges, 5000); // 5 sec delayed initial boot sync
    }
  }
};
