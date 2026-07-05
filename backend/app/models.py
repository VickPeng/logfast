from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    github_id = Column(Integer, unique=True, nullable=False)
    github_login = Column(String(255), nullable=False)
    github_email = Column(String(255), nullable=True)
    github_avatar = Column(String(512), nullable=True)
    github_token = Column(String(255), nullable=True)
    plan = Column(String(20), default="free")  # free, starter, pro
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    repositories = relationship("Repository", back_populates="owner")


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    github_repo_id = Column(Integer, nullable=False)
    full_name = Column(String(255), nullable=False)  # e.g. "owner/repo"
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    private = Column(Boolean, default=False)
    webhook_id = Column(Integer, nullable=True)
    webhook_secret = Column(String(255), nullable=True)
    custom_domain = Column(String(255), nullable=True)
    activated = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="repositories")
    changelogs = relationship(
        "Changelog",
        back_populates="repository",
        cascade="all, delete-orphan",
        order_by="Changelog.published_at.desc()",
    )


class Changelog(Base):
    __tablename__ = "changelogs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    version = Column(String(50), nullable=True)  # e.g. "v1.2.0"
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)  # Markdown content
    raw_commits = Column(JSON, nullable=True)  # Raw commit data used for generation
    status = Column(String(20), default="draft")  # draft, published
    published_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    repository = relationship("Repository", back_populates="changelogs")
