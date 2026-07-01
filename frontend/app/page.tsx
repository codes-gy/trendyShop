export default function HomePage() {
    return (
        <div className="bg-zinc-50 text-zinc-900 font-sans min-h-screen">
            <header
                className="border-b border-zinc-200/80 bg-white/80 backdrop-blur-md z-50 sticky top-0 px-6 py-4 flex items-center justify-between">
                <div className="text-xl font-black tracking-widest text-zinc-900">
                    STUDIO.🛍️
                </div>
                <nav className="hidden md:flex space-x-8 text-sm text-zinc-600 font-medium">
                    <a href="#" className="hover:text-black transition">NEW</a>
                    <a href="#" className="hover:text-black transition">SHOP</a>
                    <a href="#" className="hover:text-black transition">COLLECTION</a>
                    <a href="#" className="text-red-500 font-semibold hover:text-red-600 transition">SALE %</a>
                </nav>
                <div className="flex items-center space-x-4 text-sm font-medium">
                    <button className="hover:underline text-zinc-500">로그인</button>
                    <button
                        className="bg-zinc-900 text-white px-4 py-2 rounded-full hover:bg-zinc-600 transition shadow-sm">장바구니
                    </button>
                </div>
            </header>
            <section className="px-6 py-8 max-w-6xl mx-auto">
                <div
                    className="bg-zinc-900 text-white rounded-3xl overflow-hidden relative min-h-[500px] flex flex-col justify-end p-8 md:p-16 shadow-xl">
dd
                </div>
            </section>

        </div>
    );
}