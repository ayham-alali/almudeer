import { Building2, Loader2 } from 'lucide-react';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function SplashScreen() {
  const navigate = useNavigate();

  useEffect(() => {
    // Navigate to Login after 2 seconds to simulate app loading
    const timer = setTimeout(() => {
      navigate('/login');
    }, 2000);
    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen w-full bg-gray-900 text-white p-4 text-center">
      <div className="flex flex-col items-center animate-pulse">
        <div className="bg-blue-600 p-4 rounded-2xl mb-6 shadow-lg shadow-blue-500/20">
          <Building2 className="w-16 h-16 text-white" />
        </div>
        <h1 className="text-4xl font-bold font-sans tracking-tight mb-2">المدير</h1>
        <p className="text-gray-400 mb-12">نظام إدارة متكامل</p>
        
        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    </div>
  );
}
