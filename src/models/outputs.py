"""Pydantic models for agent outputs."""
from typing import List, Optional
from pydantic import BaseModel, Field


class ParsedProduct(BaseModel):
    """Structured product data."""
    product_name: str
    concentration: Optional[str] = None
    skin_type: Optional[str] = None
    key_ingredients: Optional[str] = None
    benefits: Optional[str] = None
    how_to_use: Optional[str] = None
    side_effects: Optional[str] = None
    price: Optional[str] = None
    price_in_inr: Optional[str] = None


class ProductDescription(BaseModel):
    """Product description output."""
    title: str
    description: str
    highlights: List[str] = Field(default_factory=list)
    usage_instructions: Optional[str] = None


class FAQ(BaseModel):
    """Single FAQ item with category."""
    question: str
    answer: str
    category: str = Field(
        description="Category: Informational, Safety, Usage, Purchase, or Comparison"
    )


class FAQPage(BaseModel):
    """FAQ page output with minimum 15 FAQs."""
    faqs: List[FAQ] = Field(min_length=15, description="Minimum 15 FAQs required")


class SimilarProduct(BaseModel):
    """Similar product information."""
    brand: str
    product_name: str
    key_features: str
    price: str
    rating: float
    rating_source: str = "estimated"
    differentiators: str


class ComparisonAnalysis(BaseModel):
    """Product comparison analysis."""
    comparison_summary: str
    feature_comparison: List[dict] = Field(default_factory=list)
    price_analysis: dict = Field(default_factory=dict)
    recommendations: dict = Field(default_factory=dict)
    best_value_pick: dict = Field(default_factory=dict)


class ProductComparison(BaseModel):
    """Complete product comparison output."""
    product_data: ParsedProduct
    comparison_basis: dict
    similar_products: List[SimilarProduct]
    analysis: ComparisonAnalysis
