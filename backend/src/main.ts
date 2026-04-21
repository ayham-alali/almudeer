import 'reflect-metadata';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe } from '@nestjs/common';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  app.enableCors({
    origin: ['https://almudeer.royaraqamia.com', 'http://localhost:3000', 'http://localhost:5173'],
    credentials: true,
  });
  
  app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }));
  
  const port = process.env.PORT || 8080;
  await app.listen(port, '0.0.0.0');
  console.log(`Application is running on: http://localhost:${port}`);
}

bootstrap();
