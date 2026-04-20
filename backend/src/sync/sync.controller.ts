import { Controller, Post, Body, UseGuards } from '@nestjs/common';
import { SyncService } from './sync.service';
import type { SyncPayload } from './sync.service';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { CurrentUser } from '../auth/decorators/current-user.decorator';

@Controller('sync')
@UseGuards(JwtAuthGuard)
export class SyncController {
  constructor(private readonly syncService: SyncService) {}

  @Post('push')
  async pushData(@CurrentUser() user: any, @Body() payload: SyncPayload) {
    // user.id comes from the decoded JWT token payload via JwtStrategy
    return this.syncService.pushSync(user.id, payload);
  }
}
