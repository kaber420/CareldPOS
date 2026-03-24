import { writable, derived } from 'svelte/store';

function createCart() {
  const { subscribe, set, update } = writable([]);

  return {
    subscribe,
    addItem: (item) => update(items => {
      // Unique key based on type + id
      const itemKey = `${item.type || 'product'}-${item.id}`;
      const existing = items.find(i => `${i.type || 'product'}-${i.id}` === itemKey);
      
      // If it's a repair, it's unique and only quantity 1
      if (item.type === 'repair') {
        if (existing) return items;
        return [...items, { ...item, quantity: 1, unit_price: item.price }];
      }

      // If it's a product, check stock
      const stock = item.stock_quantity || item.max_quantity || 0;
      if (existing) {
        if (existing.quantity >= stock) return items;
        return items.map(i => `${i.type || 'product'}-${i.id}` === itemKey 
          ? { ...i, quantity: i.quantity + 1 } 
          : i
        );
      }
      
      if (stock <= 0) return items;
      return [...items, { ...item, quantity: 1, unit_price: item.price || item.unit_price }];
    }),
    removeItem: (id, type = 'product') => update(items => 
      items.filter(i => !(`${i.type || 'product'}-${i.id}` === `${type}-${id}`))
    ),
    updateQuantity: (id, type, quantity) => update(items => {
      const itemKey = `${type || 'product'}-${id}`;
      const item = items.find(i => `${i.type || 'product'}-${i.id}` === itemKey);
      if (!item) return items;
      
      if (quantity <= 0) return items.filter(i => `${i.type || 'product'}-${i.id}` !== itemKey);
      
      // Repairs cannot change quantity
      if (item.type === 'repair') return items;

      const stock = item.stock_quantity || item.max_quantity || 0;
      const finalQuantity = Math.min(quantity, stock);
      
      return items.map(i => `${i.type || 'product'}-${i.id}` === itemKey 
        ? { ...i, quantity: finalQuantity } 
        : i
      );
    }),
    clear: () => set([]),
  };
}

export const cart = createCart();

export const cartTotal = derived(cart, ($cart) => {
  return $cart.reduce((total, item) => total + ((item.unit_price || 0) * item.quantity), 0);
});

export const cartItemsCount = derived(cart, ($cart) => {
  return $cart.reduce((count, item) => count + item.quantity, 0);
});
