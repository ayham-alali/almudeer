import { Injectable, NotFoundException, Logger } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { User, UserStatus } from '@prisma/client';
import * as bcrypt from 'bcrypt';

@Injectable()
export class UsersService {
  private readonly logger = new Logger(UsersService.name);
  
  constructor(private readonly prisma: PrismaService) {
    this.logger.log('UsersService instantiated, prisma:', !!prisma);
  }

  async createUser(data: { fullName: string; username: string; email: string; passwordHash: string }): Promise<User> {
    const trialEndsAt = new Date();
    trialEndsAt.setDate(trialEndsAt.getDate() + 14); // 14 days trial

    return this.prisma.user.create({
      data: {
        fullName: data.fullName,
        username: data.username,
        email: data.email,
        passwordHash: data.passwordHash,
        status: UserStatus.PENDING,
        trialEndsAt,
      },
    });
  }

  async findByEmailOrUsername(identifier: string): Promise<User | null> {
    return this.prisma.user.findFirst({
      where: {
        OR: [
          { email: identifier },
          { username: identifier },
        ],
      },
    });
  }
  
  async findById(id: string): Promise<User | null> {
    return this.prisma.user.findUnique({
      where: { id },
    });
  }

  async updateStatus(id: string, status: UserStatus): Promise<User> {
    return this.prisma.user.update({
      where: { id },
      data: { status },
    });
  }

  async updatePassword(id: string, newHashedPassword: string): Promise<User> {
    return this.prisma.user.update({
      where: { id },
      data: { passwordHash: newHashedPassword },
    });
  }
}
