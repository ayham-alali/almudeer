import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe } from '@nestjs/common';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  // Specific CORS config for frontend support on Railway
  app.enableCors({
    origin: ['https://almudeer.royaraqamia.com', 'http://localhost:3000', 'http://localhost:5173'],
    credentials: true,
  });
  
  // Global validation pipe for DTO validation
  app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }));
  
  // Railway requires binding to a dynamic port
  const port = process.env.PORT || 8080;
  await app.listen(port, '0.0.0.0');
  console.log(`Application is running on: http://localhost:${port}`);
}

bootstrap();
