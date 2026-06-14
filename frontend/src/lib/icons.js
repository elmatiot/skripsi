// Mapping nama icon (dari seed kategori backend) ke lucide-svelte component.
import {
  Utensils, Car, ShoppingCart, Gamepad2, HeartPulse, GraduationCap,
  Receipt, Wallet, Gift, TrendingUp, PlusCircle
} from 'lucide-svelte';

export const iconMap = {
  utensils: Utensils,
  car: Car,
  'shopping-cart': ShoppingCart,
  'gamepad-2': Gamepad2,
  'heart-pulse': HeartPulse,
  'graduation-cap': GraduationCap,
  receipt: Receipt,
  wallet: Wallet,
  gift: Gift,
  'trending-up': TrendingUp,
  'plus-circle': PlusCircle
};

export function iconFor(name) {
  return iconMap[name] || Receipt;
}
