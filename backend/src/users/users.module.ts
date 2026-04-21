import { Module, Logger, forwardRef } from '@nestjs/common';
import { UsersService } from './users.service';
import { PrismaModule } from '../prisma/prisma.module';

@Module({
  imports: [PrismaModule],
  providers: [UsersService],
  exports: [UsersService, PrismaModule],
})
export class UsersModule {
  private readonly logger = new Logger(UsersModule.name);
  
  constructor() {
    this.logger.log('UsersModule instantiated');
  }
}
