import Dexie, { type Table } from 'dexie';

export type SyncStatus = 'CREATED' | 'UPDATED' | 'DELETED' | 'SYNCED';

export interface Task {
  id: string; // UUID primary key
  title: string;
  description?: string;
  isCompleted: boolean;
  syncStatus: SyncStatus;
  createdAt: number;
}

export interface Note {
  id: string;
  title: string;
  content: string;
  syncStatus: SyncStatus;
  createdAt: number;
}

export interface Customer {
  id: string;
  name: string;
  phone?: string;
  address?: string;
  syncStatus: SyncStatus;
  createdAt: number;
}

class AlModeerDatabase extends Dexie {
  tasks!: Table<Task, string>;
  notes!: Table<Note, string>;
  customers!: Table<Customer, string>;

  constructor() {
    super('AlModeerDB');
    
    // We only index properties that we will query against.
    // 'id' is the primary key. 'syncStatus' is indexed to easily query unsynced records.
    this.version(1).stores({
      tasks: 'id, syncStatus',
      notes: 'id, syncStatus',
      customers: 'id, syncStatus'
    });
  }
}

export const db = new AlModeerDatabase();
