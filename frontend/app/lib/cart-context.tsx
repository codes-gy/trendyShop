"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

export interface CartItem {
  id: string;
  title: string;
  option: string;
  price: number;
  discountPrice: number;
  quantity: number;
  imgText: string;
  status: "stock-alert" | "normal";
  deliveryType: string;
}

interface CartContextValue {
  items: CartItem[];
  itemCount: number;
  addItem: (item: Omit<CartItem, "quantity"> & { quantity?: number }) => void;
  removeItem: (id: string) => void;
  removeMany: (ids: string[]) => void;
  changeQuantity: (id: string, delta: number) => void;
  clear: () => void;
}

const CartContext = createContext<CartContextValue | null>(null);

const STORAGE_KEY = "trndy-cart-items";

export function CartProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<CartItem[]>([]);
  const [hydrated, setHydrated] = useState(false);

  // 최초 마운트 시 localStorage에서 이전 장바구니 상태를 복원합니다.
  // (SSR과의 하이드레이션 불일치를 피하려면 localStorage 읽기는 반드시 useEffect
  // 안에서, 마운트 이후에 해야 합니다 — 그래서 여기서의 setState는 의도된 것입니다.)
  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      // eslint-disable-next-line react-hooks/set-state-in-effect -- localStorage 하이드레이션은 마운트 이후에만 가능합니다.
      if (raw) setItems(JSON.parse(raw));
    } catch {
      // 사파리 프라이빗 모드 등 localStorage 접근이 막힌 환경은 조용히 무시하고 빈 장바구니로 시작합니다.
    } finally {
      setHydrated(true);
    }
  }, []);

  // items가 바뀔 때마다 localStorage에 반영합니다. (하이드레이션 이전에는 덮어쓰지 않도록 방지)
  useEffect(() => {
    if (!hydrated) return;
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    } catch {
      // 저장 용량 초과 등은 무시합니다.
    }
  }, [items, hydrated]);

  const addItem: CartContextValue["addItem"] = (item) => {
    setItems((prev) => {
      const existing = prev.find((i) => i.id === item.id);
      if (existing) {
        return prev.map((i) =>
          i.id === existing.id
            ? { ...i, quantity: Math.min(10, i.quantity + (item.quantity ?? 1)) }
            : i,
        );
      }
      return [...prev, { ...item, quantity: item.quantity ?? 1 }];
    });
  };

  const removeItem = (id: string) => {
    setItems((prev) => prev.filter((i) => i.id !== id));
  };

  const removeMany = (ids: string[]) => {
    const idSet = new Set(ids);
    setItems((prev) => prev.filter((i) => !idSet.has(i.id)));
  };

  const changeQuantity = (id: string, delta: number) => {
    setItems((prev) =>
      prev.map((i) =>
        i.id === id
          ? { ...i, quantity: Math.max(1, Math.min(10, i.quantity + delta)) }
          : i,
      ),
    );
  };

  const clear = () => setItems([]);

  const itemCount = items.reduce((acc, i) => acc + i.quantity, 0);

  return (
    <CartContext.Provider
      value={{
        items,
        itemCount,
        addItem,
        removeItem,
        removeMany,
        changeQuantity,
        clear,
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart(): CartContextValue {
  const ctx = useContext(CartContext);
  if (!ctx) {
    throw new Error("useCart()는 CartProvider 내부에서만 사용할 수 있습니다.");
  }
  return ctx;
}
