import { Global, Module, Logger } from '@nestjs/common';
import { PrismaService } from './prisma.service';

@Global()
@Module({
  providers: [PrismaService],
  exports: [PrismaService],
})
export class PrismaModule {
  private readonly logger = new Logger(PrismaModule.name);
  
  constructor() {
    this.logger.log('PrismaModule instantiated');
  }
}
