import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Loader2, ShieldCheck, Copy } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';

export function TwoFactorSetup() {
  const [loading, setLoading] = useState(false);
  const [setupData, setSetupData] = useState<{ secret: string, qr_code: string, recovery_code: string } | null>(null);
  const [otp, setOtp] = useState('');
  const [isVerified, setIsVerified] = useState(false);
  const { setup2FA, verify2FASetup } = useAuth();

  const handleSetup = async () => {
    setLoading(true);
    try {
      const data = await setup2FA();
      setSetupData(data);
    } catch (err: any) {
      toast.error(err?.message || 'Failed to start 2FA setup');
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async () => {
    if (!otp || otp.length < 6) {
      toast.error('Please enter a valid 6-digit code');
      return;
    }
    setLoading(true);
    try {
      await verify2FASetup(otp);
      setIsVerified(true);
      toast.success('Two-Factor Authentication enabled successfully!');
    } catch (err: any) {
      toast.error(err?.message || 'Invalid code');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard');
  };

  if (isVerified) {
    return (
      <div className="flex flex-col items-center justify-center p-6 bg-primary/5 rounded-xl border border-primary/20 text-center">
        <ShieldCheck className="w-12 h-12 text-primary mb-4" />
        <h3 className="font-semibold text-lg mb-2">2FA is Enabled</h3>
        <p className="text-sm text-muted-foreground">Your account is now protected with Two-Factor Authentication.</p>
      </div>
    );
  }

  if (!setupData) {
    return (
      <div className="p-6 bg-card rounded-xl border">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-primary/10 rounded-full">
            <ShieldCheck className="w-6 h-6 text-primary" />
          </div>
          <div className="flex-1">
            <h3 className="font-semibold text-lg mb-1">Two-Factor Authentication</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Add an extra layer of security to your account by enabling 2FA. You'll need an authenticator app like Google Authenticator or Authy.
            </p>
            <Button onClick={handleSetup} disabled={loading}>
              {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
              Enable 2FA
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-card rounded-xl border space-y-6">
      <div>
        <h3 className="font-semibold text-lg mb-1">Setup Two-Factor Authentication</h3>
        <p className="text-sm text-muted-foreground">Follow these steps to complete the setup.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-8 items-start">
        <div className="space-y-4">
          <div>
            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-primary/10 text-primary text-xs font-bold mr-2">1</span>
            <span className="text-sm font-medium">Scan QR Code</span>
            <p className="text-sm text-muted-foreground mt-1 ml-8">Open your authenticator app and scan this QR code.</p>
          </div>
          <div className="ml-8 p-4 bg-white rounded-lg border inline-block">
            <img src={setupData.qr_code} alt="QR Code" className="w-40 h-40" />
          </div>
          
          <div className="ml-8">
            <p className="text-xs text-muted-foreground mb-2">Or enter this secret manually:</p>
            <div className="flex items-center gap-2">
              <code className="px-2 py-1 bg-muted rounded text-xs select-all">{setupData.secret}</code>
              <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => copyToClipboard(setupData.secret)}>
                <Copy className="w-3 h-3" />
              </Button>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="space-y-4">
            <div>
              <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-primary/10 text-primary text-xs font-bold mr-2">2</span>
              <span className="text-sm font-medium">Save Recovery Code</span>
              <p className="text-sm text-muted-foreground mt-1 ml-8">Save this recovery code in a safe place. You can use it to log in if you lose access to your authenticator app.</p>
            </div>
            <div className="ml-8 flex items-center gap-2">
              <code className="px-3 py-2 bg-destructive/10 text-destructive font-bold rounded select-all">{setupData.recovery_code}</code>
              <Button variant="outline" size="icon" onClick={() => copyToClipboard(setupData.recovery_code)}>
                <Copy className="w-4 h-4" />
              </Button>
            </div>
          </div>

          <div className="space-y-4 pt-4 border-t">
            <div>
              <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-primary/10 text-primary text-xs font-bold mr-2">3</span>
              <span className="text-sm font-medium">Verify Code</span>
              <p className="text-sm text-muted-foreground mt-1 ml-8">Enter the 6-digit code from your app to verify the setup.</p>
            </div>
            <div className="ml-8 flex gap-2">
              <Input 
                value={otp} 
                onChange={e => setOtp(e.target.value)} 
                placeholder="000000" 
                maxLength={6}
                className="max-w-[150px]"
              />
              <Button onClick={handleVerify} disabled={loading || otp.length < 6}>
                {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                Verify
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
