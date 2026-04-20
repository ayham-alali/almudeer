import { Injectable, Logger, OnModuleInit } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as nodemailer from 'nodemailer';

@Injectable()
export class EmailService implements OnModuleInit {
  private transporter: nodemailer.Transporter;
  private readonly logger = new Logger(EmailService.name);

  constructor(private configService: ConfigService) {}

  onModuleInit() {
    const host = this.configService.get<string>('SMTP_HOST') || 'smtp.resend.com';
    const port = this.configService.get<number>('SMTP_PORT') || 465;
    const secure = this.configService.get<string>('SMTP_USE_TLS') === 'true' || port === 465;
    const user = this.configService.get<string>('SMTP_USERNAME') || '';
    const pass = this.configService.get<string>('SMTP_PASSWORD') || '';

    this.transporter = nodemailer.createTransport({
      host,
      port,
      secure,
      auth: {
        user,
        pass,
      },
    });
  }

  async sendOtpEmail(to: string, otp: string) {
    const fromEmail = this.configService.get<string>('FROM_EMAIL') || 'onboarding@resend.dev';
    const fromName = this.configService.get<string>('FROM_NAME') || 'Al-Mudeer';
    
    const html = `
      <div dir="rtl" style="font-family: Arial, sans-serif; padding: 20px; line-height: 1.6; text-align: right;">
        <p>مرحباً بك في المدير،</p>
        <p>رمز التحقق الخاص بك في تطبيق المدير هو:</p>
        <div style="font-size: 24px; font-weight: bold; padding: 10px; background-color: #f4f4f4; display: inline-block; letter-spacing: 2px;">
          ${otp}
        </div>
        <p>هذا الرمز صالح لمدة 10 دقائق.</p>
        <p>إذا لم تطلب هذا الرمز، يرجى تجاهل هذه الرسالة.</p>
      </div>
    `;

    try {
      await this.transporter.sendMail({
        from: `"${fromName}" <${fromEmail}>`,
        to,
        subject: 'رمز التحقق - تطبيق المدير',
        html,
      });
      this.logger.log(`OTP Email sent to ${to}`);
    } catch (error) {
      this.logger.error(`Failed to send email to ${to}`, error);
    }
  }
}
