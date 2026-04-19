import { IsEmail, IsString, MinLength, IsNotEmpty } from 'class-validator';

export class RegisterDto {
  @IsString()
  @IsNotEmpty()
  fullName!: string;

  @IsString()
  @IsNotEmpty()
  username!: string;

  @IsEmail()
  email!: string;

  @IsString()
  @MinLength(6)
  password!: string;
}

export class LoginDto {
  @IsString()
  @IsNotEmpty()
  identifier!: string; // email or username

  @IsString()
  @IsNotEmpty()
  password!: string;
}

export class VerifyOtpDto {
  @IsEmail()
  email!: string;

  @IsString()
  @IsNotEmpty()
  otp!: string;
}

export class ForgotPasswordDto {
  @IsEmail()
  email!: string;
}

export class ResetPasswordDto {
  @IsEmail()
  email!: string;

  @IsString()
  @IsNotEmpty()
  otp!: string;

  @IsString()
  @MinLength(6)
  newPassword!: string;
}
