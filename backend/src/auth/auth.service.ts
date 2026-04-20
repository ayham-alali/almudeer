import { Injectable, UnauthorizedException, ForbiddenException, BadRequestException, NotFoundException } from '@nestjs/common';
import { UsersService } from '../users/users.service';
import { JwtService } from '@nestjs/jwt';
import * as bcrypt from 'bcrypt';
import { UserStatus } from '@prisma/client';
import { RegisterDto, LoginDto, VerifyOtpDto, ForgotPasswordDto, ResetPasswordDto } from './dto/auth.dto';
import { EmailService } from '../email/email.service';

interface OtpData {
  otp: string;
  expiresAt: Date;
}

@Injectable()
export class AuthService {
  // Using an in-memory map for cache (could be swapped with Redis in production)
  private readonly otpCache = new Map<string, OtpData>();

  constructor(
    private readonly usersService: UsersService,
    private readonly jwtService: JwtService,
    private readonly emailService: EmailService,
  ) {}

  private generateVerificationOtp(): string {
    return Math.floor(100000 + Math.random() * 900000).toString();
  }

  async register(dto: RegisterDto) {
    const existingUser = await this.usersService.findByEmailOrUsername(dto.email) ||
                         await this.usersService.findByEmailOrUsername(dto.username);
    if (existingUser) {
      throw new BadRequestException('Email or username already in use');
    }

    const saltRounds = 10;
    const passwordHash = await bcrypt.hash(dto.password, saltRounds);

    const user = await this.usersService.createUser({
      fullName: dto.fullName,
      username: dto.username,
      email: dto.email,
      passwordHash,
    });

    const otp = this.generateVerificationOtp();
    
    // Set 10 minute expiry
    const expiresAt = new Date();
    expiresAt.setMinutes(expiresAt.getMinutes() + 10);
    
    this.otpCache.set(user.email, { otp, expiresAt });

    // Real Email sending
    await this.emailService.sendOtpEmail(user.email, otp);

    return { message: 'Registration successful. Please verify your email with the OTP sent.' };
  }

  async verifyEmailOtp(dto: VerifyOtpDto) {
    const cachedData = this.otpCache.get(dto.email);

    if (!cachedData) {
      throw new BadRequestException('Invalid or expired OTP');
    }

    if (new Date() > cachedData.expiresAt) {
      this.otpCache.delete(dto.email);
      throw new BadRequestException('OTP has expired');
    }

    if (cachedData.otp !== dto.otp) {
      throw new BadRequestException('Invalid OTP');
    }

    // OTP is valid
    const user = await this.usersService.findByEmailOrUsername(dto.email);
    if (!user) throw new NotFoundException('User not found');

    await this.usersService.updateStatus(user.id, UserStatus.ACTIVE);
    this.otpCache.delete(dto.email);

    const payload = { sub: user.id, username: user.username, status: UserStatus.ACTIVE };
    return {
      message: 'Email verified successfully',
      accessToken: this.jwtService.sign(payload),
    };
  }

  async login(dto: LoginDto) {
    const user = await this.usersService.findByEmailOrUsername(dto.identifier);
    if (!user) throw new UnauthorizedException('Invalid credentials');

    const isPasswordValid = await bcrypt.compare(dto.password, user.passwordHash);
    if (!isPasswordValid) throw new UnauthorizedException('Invalid credentials');

    if (user.status === UserStatus.PENDING) {
      throw new UnauthorizedException('Account pending admin approval or email verification');
    }

    if (user.status === UserStatus.EXPIRED || (user.trialEndsAt && new Date() > user.trialEndsAt)) {
      throw new ForbiddenException('Trial expired');
    }

    const payload = { sub: user.id, username: user.username, status: user.status };
    return {
      accessToken: this.jwtService.sign(payload),
    };
  }

  async forgotPassword(dto: ForgotPasswordDto) {
    const user = await this.usersService.findByEmailOrUsername(dto.email);
    if (!user) {
      throw new NotFoundException('User not found');
    }

    const otp = this.generateVerificationOtp();
    const expiresAt = new Date();
    expiresAt.setMinutes(expiresAt.getMinutes() + 10);
    
    // Prefix cache key to separate from email verification OTPs
    this.otpCache.set(`reset_${dto.email}`, { otp, expiresAt });

    // Real Email sending
    await this.emailService.sendOtpEmail(user.email, otp);

    return { message: 'If the email exists, a reset OTP has been sent.' };
  }

  async resetPassword(dto: ResetPasswordDto) {
    const cachedData = this.otpCache.get(`reset_${dto.email}`);

    if (!cachedData || new Date() > cachedData.expiresAt || cachedData.otp !== dto.otp) {
      throw new BadRequestException('Invalid or expired OTP');
    }

    const user = await this.usersService.findByEmailOrUsername(dto.email);
    if (!user) throw new NotFoundException('User not found');

    const passwordHash = await bcrypt.hash(dto.newPassword, 10);
    await this.usersService.updatePassword(user.id, passwordHash);

    this.otpCache.delete(`reset_${dto.email}`);

    return { message: 'Password has been reset successfully' };
  }
}
