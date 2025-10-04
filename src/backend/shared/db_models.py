"""
SQLAlchemy Database Models
"""

from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, ForeignKey, Text, ARRAY, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

# ============= Users =============

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String)
    monthly_income = Column(Numeric(12, 2))
    financial_goals = Column(ARRAY(Text))
    risk_tolerance = Column(String, default='moderate')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    budgets = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")
    category_preferences = relationship("UserCategoryPreference", back_populates="user", cascade="all, delete-orphan")
    merchant_overrides = relationship("UserMerchantOverride", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("risk_tolerance IN ('conservative', 'moderate', 'aggressive')", name='check_risk_tolerance'),
    )

# ============= Categories =============

class Category(Base):
    __tablename__ = 'categories'

    id = Column(String, primary_key=True)  # Custom IDs like 'cat_housing'
    name = Column(String, unique=True, nullable=False)
    necessity_score = Column(Integer, nullable=False)
    default_allocation_percent = Column(Numeric(5, 2))
    parent_category_id = Column(String, ForeignKey('categories.id'))
    is_system = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    rules = relationship("CategoryRule", back_populates="category", cascade="all, delete-orphan")
    budget_allocations = relationship("BudgetAllocation", back_populates="category")

    __table_args__ = (
        CheckConstraint("necessity_score BETWEEN 1 AND 10", name='check_necessity_score'),
    )

class CategoryRule(Base):
    __tablename__ = 'category_rules'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(String, ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    keywords = Column(ARRAY(Text), default=[])
    merchant_patterns = Column(ARRAY(Text), default=[])
    match_type = Column(String, default='substring')
    priority = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    category = relationship("Category", back_populates="rules")

    __table_args__ = (
        CheckConstraint("match_type IN ('exact', 'substring', 'regex')", name='check_match_type'),
    )

# ============= User Preferences =============

class UserCategoryPreference(Base):
    __tablename__ = 'user_category_preferences'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    category_id = Column(String, ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)
    custom_priority = Column(Integer)
    monthly_limit = Column(Numeric(12, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="category_preferences")

    __table_args__ = (
        CheckConstraint("custom_priority BETWEEN 1 AND 10", name='check_custom_priority'),
    )

class UserMerchantOverride(Base):
    __tablename__ = 'user_merchant_overrides'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    merchant = Column(String, nullable=False)
    category_id = Column(String, ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="merchant_overrides")

# ============= Budgets =============

class Budget(Base):
    __tablename__ = 'budgets'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    month = Column(String, nullable=False)  # Format: "2025-10"
    total_income = Column(Numeric(12, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="budgets")
    allocations = relationship("BudgetAllocation", back_populates="budget", cascade="all, delete-orphan")

class BudgetAllocation(Base):
    __tablename__ = 'budget_allocations'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    budget_id = Column(UUID(as_uuid=True), ForeignKey('budgets.id', ondelete='CASCADE'), nullable=False)
    category_id = Column(String, ForeignKey('categories.id'), nullable=False)
    allocated_amount = Column(Numeric(12, 2), nullable=False)
    spent_amount = Column(Numeric(12, 2), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    budget = relationship("Budget", back_populates="allocations")
    category = relationship("Category", back_populates="budget_allocations")

# ============= Expenses =============

class Expense(Base):
    __tablename__ = 'expenses'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    category_id = Column(String, ForeignKey('categories.id'))
    description = Column(Text)
    merchant = Column(String)
    date = Column(DateTime(timezone=True), server_default=func.now())
    is_recurring = Column(Boolean, default=False)
    ai_suggested_category = Column(String, ForeignKey('categories.id'))
    confidence_score = Column(Numeric(3, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="expenses")

class RecurringExpense(Base):
    __tablename__ = 'recurring_expenses'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    category_id = Column(String, ForeignKey('categories.id'))
    description = Column(Text)
    frequency = Column(String, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("frequency IN ('daily', 'weekly', 'monthly', 'yearly')", name='check_frequency'),
    )

# ============= Chat Messages =============

class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    message_metadata = Column('metadata', Text)  # JSON stored as text, renamed to avoid conflict

    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant')", name='check_role'),
    )
