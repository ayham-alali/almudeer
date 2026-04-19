import { Injectable, UnauthorizedException } from '@nestjs/common';
import { PassportStrategy } from '@nestjs/passport';
import { ExtractJwt, Strategy } from 'passport-jwt';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class JwtStrategy extends PassportStrategy(Strategy) {
  constructor(private readonly configService: ConfigService) {
    super({
      jwtFromRequest: ExtractJwt.fromAuthHeaderAsBearerToken(),
      ignoreExpiration: false,
      secretOrKey: configService.get<string>('JWT_SECRET') || 'defaultSecretChangeThisInProduction',
    });
  }

  async validate(payload: { sub: string; username: string; status: string }) {
    // This payload will be injected into request.user via our @CurrentUser() decorator
    return { id: payload.sub, username: payload.username, status: payload.status };
  }
}
