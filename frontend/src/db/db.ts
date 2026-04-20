import Dexie, { type Table } from 'dexie';

export type SyncStatus = 'CREATED' | 'UPDATED' | 'DELETED' | 'SYNCED';

export type TaskPriority = 'HIGH' | 'MEDIUM' | 'LOW';
export type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
export type TaskRecurrence = 'NONE' | 'DAILY' | 'WEEKLY' | 'MONTHLY';

export interface Task {
  id: string; // UUID primary key
  title: string;
  description?: string;
  priority: TaskPriority;
  status: TaskStatus;
  dateTime?: string;
  alarmEnabled: boolean;
  recurrence: TaskRecurrence;
  isFixed?: boolean;
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
  description?: string;
  defaultCurrency?: string;
  syncStatus: SyncStatus;
  createdAt: number;
}

export type TransactionType = 'FOR_ME' | 'ON_ME'; // For Me (له) vs On Me (عليه)

export interface LedgerTransaction {
  id: string;
  customerId: string;
  type: TransactionType;
  amount: number;
  currency: string;
  notes?: string;
  date: number;
  syncStatus: SyncStatus;
  createdAt: number;
}

class AlModeerDatabase extends Dexie {
  tasks!: Table<Task, string>;
  notes!: Table<Note, string>;
  customers!: Table<Customer, string>;
  ledger!: Table<LedgerTransaction, string>;

  constructor() {
    super('AlModeerDB');
    
    // We only index properties that we will query against.
    // 'id' is the primary key. 'syncStatus' is indexed to easily query unsynced records.
    this.version(2).stores({
      tasks: 'id, syncStatus',
      notes: 'id, syncStatus',
      customers: 'id, syncStatus',
      ledger: 'id, customerId, type, date, syncStatus'
    });
  }
}

export const db = new AlModeerDatabase();
