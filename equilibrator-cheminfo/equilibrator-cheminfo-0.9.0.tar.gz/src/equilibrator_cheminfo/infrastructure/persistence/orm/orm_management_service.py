# Copyright (c) 2021, Moritz E. Beber.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Provide a management service for handling a database."""


from sqlalchemy import create_engine

from .orm_base import ORMBase, ORMSession


class ORMManagementService:
    """Define a management service for handling a database."""

    @classmethod
    def create_session(cls, db_url: str) -> ORMSession:
        """Create a SQLAlchemy session with an active database connection."""
        return ORMSession(bind=create_engine(db_url))

    @classmethod
    def initialize(cls, db_url) -> None:
        """Initialize a suitable database schema destructively, dropping all tables."""
        session = cls.create_session(db_url)
        ORMBase.metadata.drop_all(session.bind)
        ORMBase.metadata.create_all(session.bind)
