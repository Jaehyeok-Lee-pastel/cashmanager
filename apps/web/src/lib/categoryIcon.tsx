import {
  Bus,
  Clapperboard,
  Coffee,
  CreditCard,
  Gift,
  GraduationCap,
  Home,
  Package,
  Pill,
  ShoppingBag,
  ShoppingCart,
  Smartphone,
  Tag,
  Utensils,
  Wallet,
  type LucideIcon,
} from "lucide-react";

// Maps a category name to a consistent vector icon (designed look, OS-agnostic).
const ICON_BY_NAME: Record<string, LucideIcon> = {
  "식비": Utensils,
  "카페/간식": Coffee,
  "교통": Bus,
  "생활/마트": ShoppingCart,
  "쇼핑": ShoppingBag,
  "문화/여가": Clapperboard,
  "건강/의료": Pill,
  "주거": Home,
  "주거/통신": Home,
  "통신": Smartphone,
  "경조사": Gift,
  "교육": GraduationCap,
  "카드대금": CreditCard,
  "기타지출": Package,
  "수입": Wallet,
};

interface Props {
  name: string | null;
  size?: number;
  color?: string;
}

export function CategoryIcon({ name, size = 18, color }: Props) {
  const Icon = (name && ICON_BY_NAME[name]) || Tag;
  return <Icon size={size} color={color} strokeWidth={2} aria-hidden />;
}
