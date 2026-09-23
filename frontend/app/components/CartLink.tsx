"use client";

import Link from "next/link";
import { useCart } from "../lib/cart-context";

export default function CartLink() {
  const { itemCount } = useCart();

  return (
    <Link
      href="/cart"
      className="relative rounded-full bg-zinc-950 px-4 py-2 text-white shadow-md transition hover:bg-zinc-800"
    >
      CART <span className="ml-1 font-black text-rose-400">{itemCount}</span>
    </Link>
  );
}
