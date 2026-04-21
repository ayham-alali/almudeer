import { Module, Logger } from '@nestjs/common';
import { UsersService } from './users.service';

@Module({
  providers: [UsersService],
  exports: [UsersService],
})
export class UsersModule {
  private readonly logger = new Logger(UsersModule.name);
  
  constructor() {
    this.logger.log('UsersModule instantiated');
  }
}
