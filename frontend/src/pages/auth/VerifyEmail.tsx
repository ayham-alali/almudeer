import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { ShieldCheck, RefreshCw } from 'lucide-react';
import { cn } from '../../lib/utils';

export default function VerifyEmail() {
  const navigate = useNavigate();
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [isVerifying, setIsVerifying] = useState(false);
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    // Focus first input on mount
    if (inputRefs.current[0]) {
      inputRefs.current[0].focus();
    }
  }, []);

  const handleChange = (index: number, value: string) => {
    if (value.length > 1) value = value.slice(-1); // Only accept 1 char
    
    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    // Auto-advance logic (RTL aware, next visual box is right-to-left usually... 
    // but array indexing implies index 0 is first logically. We'll advance array index)
    if (value && index < 5 && inputRefs.current[index + 1]) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      // Auto reverse
      inputRefs.current[index - 1]?.focus();
    }
  };

  const onConfirm = async () => {
    setIsVerifying(true);
    await new Promise((resolve) => setTimeout(resolve, 1500));
    setIsVerifying(false);
    navigate('/pending-approval');
  };

  const isComplete = otp.every(val => val.length === 1);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-gray-50 dark:bg-gray-900">
      <div className="w-full max-w-md p-8 space-y-8 bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 text-center">
        
        <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-500 rounded-full flex items-center justify-center mx-auto mb-2">
          <ShieldCheck className="w-8 h-8" />
        </div>

        <div className="space-y-2">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">تأكيد البريد الإلكتروني</h1>
          <p className="text-gray-500 dark:text-gray-400">
            لقد أرسلنا رمزاً مكوناً من 6 أرقام إلى بريدك الإلكتروني. الرجاء إدخاله أدناه.
          </p>
        </div>

        <div className="space-y-6 pt-4">
          <div className="flex justify-center gap-2 md:gap-3" dir="ltr">
            {otp.map((digit, idx) => (
              <input
                key={idx}
                ref={(el) => (inputRefs.current[idx] = el)}
                type="text"
                inputMode="numeric"
                maxLength={1}
                value={digit}
                onChange={(e) => handleChange(idx, e.target.value)}
                onKeyDown={(e) => handleKeyDown(idx, e)}
                className={cn(
                  "w-12 h-14 md:w-14 md:h-16 text-center text-xl md:text-2xl font-bold bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-12",
                  "focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none transition-colors",
                  "text-gray-900 dark:text-white placeholder:text-gray-400"
                )}
              />
            ))}
          </div>

          <div className="flex flex-col gap-3 pt-6">
            <Button 
              variant="primary" 
              className="w-full" 
              disabled={!isComplete}
              onClick={onConfirm}
              isLoading={isVerifying}
            >
              تأكيد
            </Button>
            
            <Button 
              variant="ghost" 
              type="button"
              className="w-full text-blue-600 dark:text-blue-400"
              leftIcon={<RefreshCw className="w-4 h-4" />}
            >
              إعادة إرسال الرمز
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
