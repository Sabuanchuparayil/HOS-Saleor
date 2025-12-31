# Verify Schema Fix

After restarting the backend, verify the marketplace queries are available:

```bash
curl -X POST https://hos-saleor-production.up.railway.app/graphql/ \
  -H "Content-Type: application/json" \
  -H "Origin: https://hos-storefront-production.up.railway.app" \
  -d '{"query":"{ __type(name: \"Query\") { fields { name } } }"}' \
  | python3 -m json.tool | grep -E "sellers|featured"
```

You should see:
- `sellers`
- `featuredCollections` (or `featured_collections` depending on Graphene conversion)
- `featuredProducts` (or `featured_products`)

If these fields appear, the schema has been rebuilt correctly.

