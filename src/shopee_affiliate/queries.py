"""Standard GraphQL query and mutation templates for Shopee Affiliate API."""

GENERATE_SHORT_LINK_MUTATION = """
mutation generateShortLink($input: ShortLinkInput!) {
  generateShortLink(input: $input) {
    shortLink
  }
}
""".strip()

PRODUCT_OFFER_QUERY = """
query productOfferV2(
  $keyword: String
  $itemId: Int64
  $shopId: Int64
  $productCatId: Int32
  $listType: Int
  $sortType: Int
  $page: Int
  $limit: Int
  $isAMSOffer: Boolean
  $isKeySeller: Boolean
) {
  productOfferV2(
    keyword: $keyword
    itemId: $itemId
    shopId: $shopId
    productCatId: $productCatId
    listType: $listType
    sortType: $sortType
    page: $page
    limit: $limit
    isAMSOffer: $isAMSOffer
    isKeySeller: $isKeySeller
  ) {
    nodes {
      itemId
      productName
      productLink
      offerLink
      imageUrl
      commissionRate
      sellerCommissionRate
      shopeeCommissionRate
      commission
      priceMin
      priceMax
      sales
      ratingStar
      priceDiscountRate
      shopId
      shopName
      shopType
      productCatIds
      periodStartTime
      periodEndTime
    }
    pageInfo {
      page
      limit
      hasNextPage
    }
  }
}
""".strip()

SHOP_OFFER_QUERY = """
query shopOfferV2(
  $shopId: Int64
  $keyword: String
  $shopType: [Int]
  $isKeySeller: Boolean
  $sortType: Int
  $page: Int
  $limit: Int
) {
  shopOfferV2(
    shopId: $shopId
    keyword: $keyword
    shopType: $shopType
    isKeySeller: $isKeySeller
    sortType: $sortType
    page: $page
    limit: $limit
  ) {
    nodes {
      shopId
      shopName
      offerLink
      originalLink
      commissionRate
      sellerCommCoveRatio
      ratingStar
      imageUrl
      shopType
      periodStartTime
      periodEndTime
    }
    pageInfo {
      page
      limit
      hasNextPage
    }
  }
}
""".strip()

CONVERSION_REPORT_QUERY = """
query conversionReport(
  $purchaseTimeStart: Int
  $purchaseTimeEnd: Int
  $completeTimeStart: Int
  $completeTimeEnd: Int
  $shopName: String
  $shopId: Int64
  $orderId: String
  $orderStatus: String
  $limit: Int
  $scrollId: String
) {
  conversionReport(
    purchaseTimeStart: $purchaseTimeStart
    purchaseTimeEnd: $purchaseTimeEnd
    completeTimeStart: $completeTimeStart
    completeTimeEnd: $completeTimeEnd
    shopName: $shopName
    shopId: $shopId
    orderId: $orderId
    orderStatus: $orderStatus
    limit: $limit
    scrollId: $scrollId
  ) {
    nodes {
      conversionId
      purchaseTime
      clickTime
      totalCommission
      sellerCommission
      shopeeCommissionCapped
      netCommission
      buyerType
      utmContent
      device
      orders {
        orderId
        orderStatus
        shopType
        items {
          itemId
          itemName
          itemPrice
          qty
          actualAmount
          itemTotalCommission
          itemSellerCommission
          itemShopeeCommissionCapped
          displayItemStatus
          orderId
          shopId
          shopName
          completeTime
          imageUrl
          fraudStatus
        }
      }
    }
    pageInfo {
      limit
      hasNextPage
      scrollId
    }
  }
}
""".strip()

VALIDATED_REPORT_QUERY = """
query validatedReport(
  $validationId: Int64!
  $limit: Int
  $scrollId: String
) {
  validatedReport(
    validationId: $validationId
    limit: $limit
    scrollId: $scrollId
  ) {
    nodes {
      conversionId
      purchaseTime
      clickTime
      totalCommission
      sellerCommission
      shopeeCommissionCapped
      netCommission
      orders {
        orderId
        orderStatus
        shopType
        items {
          itemId
          itemName
          itemPrice
          qty
          actualAmount
          itemTotalCommission
          itemSellerCommission
          itemShopeeCommissionCapped
          displayItemStatus
          orderId
          shopId
          shopName
          completeTime
        }
      }
    }
    pageInfo {
      limit
      hasNextPage
      scrollId
    }
  }
}
""".strip()
