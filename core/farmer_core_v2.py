from dateutil.parser import parse
import datetime
from typing import Dict, List, Optional
from config.config import get_supabase_client
from core.company_core import Company
from exceptions.global_exception import GlobalException
from models.feed_calculator_model import CreateFeedCalculatorPayload, FeedCalculatorDto, UpdateFeedCalculatorPayload


class FarmerV2:
    def __init__(self):
        self.Client = get_supabase_client()
        self.Company = Company()

    # Create feed program
    def create_feed_program(self, farmer_user_profile_id: int, feed_product_id: int):

        self.update_current_active_feed_program(farmer_user_profile_id)

        self.Client.table("feed_programs").insert({
            "farmer_user_profile_id": farmer_user_profile_id,
            "feed_product_id": feed_product_id,
        }).execute()
        return None

    # Get active feed program (NOTE ONLY ONE ACTIVE PROGRAM IS ALLOWED)
    def get_active_feed_program(self, farmer_user_profile_id: int):
        response = (
            self.Client.table("feed_programs")
            .select("*")
            .eq("farmer_user_profile_id", farmer_user_profile_id)
            .eq("status", "active")
            .limit(1)
            .execute()
        )

        if not response.data or len(response.data) == 0:
            raise GlobalException(
                "There is no current active feed program.", 404)

        return response.data[0]

    # Update current active feed program (helper method when farmer switched midway without explicitly marking the current program as incomplete or complete)

    def update_current_active_feed_program(self, farmer_user_profile_id: int):
        response = (
            self.Client.table("feed_programs")
            .select("id")
            .eq("farmer_user_profile_id", farmer_user_profile_id)
            .eq("status", "active")
            .limit(1)
            .execute()
        )

        if response.data and len(response.data) > 0:
            active_id = response.data[0]["id"]
            self.Client.table("feed_programs").update({
                "status": "switched"
            }).eq("id", active_id).execute()

            return active_id

        return None

    def complete_active_feed_program(self, farmer_user_profile_id: int):
        response = (
            self.Client.table("feed_programs")
            .select("id")
            .eq("farmer_user_profile_id", farmer_user_profile_id)
            .eq("status", "active")
            .limit(1)
            .execute()
        )

        if response.data and len(response.data) > 0:
            active_id = response.data[0]["id"]
            self.Client.table("feed_programs").update({
                "status": "completed"
            }).eq("id", active_id).execute()
            return active_id

        return None

    def incomplete_active_feed_program(self, farmer_user_profile_id: int):
        response = (
            self.Client.table("feed_programs")
            .select("id")
            .eq("farmer_user_profile_id", farmer_user_profile_id)
            .eq("status", "active")
            .limit(1)
            .execute()
        )

        if response.data and len(response.data) > 0:
            active_id = response.data[0]["id"]
            self.Client.table("feed_programs").update({
                "status": "incomplete"
            }).eq("id", active_id).execute()
            return active_id

        return None

    # DASHBOARD COMPONENT DATA SECTION

    # Method to get current feed product associated with active feed program
    def get_active_feed_product(self, farmer_user_profile_id: int):
        feed_program_response = (
            self.Client.table("feed_programs")
            .select("id, feed_product_id, days_on_feed, status")
            .eq("farmer_user_profile_id", farmer_user_profile_id)
            .eq("status", "active")
            .limit(1)
            .execute()
        )

        if not feed_program_response.data:
            return None  # No active feed program

        feed_program = feed_program_response.data[0]

        # Fetch feed product details
        feed_product_response = (
            self.Client.table("feed_products")
            .select("id, name, feed_stage, age_range_start, age_range_end, goal")
            .eq("id", feed_program["feed_product_id"])
            .limit(1)
            .execute()
        )

        if not feed_product_response.data:
            return None  # No feed product found

        feed_product = feed_product_response.data[0]

        # Build DTO
        feed_product_dto = {
            "feed_program_id": feed_program["id"],
            "feed_name": feed_product["name"],
            "status": feed_program["status"],
            "feed_stage": feed_product["feed_stage"],
            "age_range_start": feed_product["age_range_start"],
            "age_range_end": feed_product["age_range_end"],
            "feed_goal": feed_product["goal"],
            "days_on_feed": feed_program["days_on_feed"],
        }

        return feed_product_dto

    # FEED CALCULATOR

    def create_feed_calculation_log(self, payload: CreateFeedCalculatorPayload) -> Dict:
        response = self.Client.table(
            "feed_calculation_logs").insert(payload).execute()
        return response.data[0] if response.data else {}

    def read_feed_calculation_log(self, farmer_user_profile_id: int) -> FeedCalculatorDto:
        response = (
            self.Client.table("feed_calculation_logs")
            .select("*")
            .eq("user_profile_id", farmer_user_profile_id)
            .execute()
        )

        print(response)

        if not response.data or len(response.data) == 0:
            raise GlobalException(
                "There is no current calculation log program.", 404)

        data = response.data[0]
        feed_calculation_log = FeedCalculatorDto(
            id=data["id"],
            farmer_user_profile_id=data["user_profile_id"],
            number_of_animals=data["number_of_animals"],
            feed_frequency=data["feed_frequency"],
            bag_size_kg=data["bag_size_kg"],
            current_stock_bags=data["current_stock_bags"],
            bag_cost_php=data["bag_cost_php"],
            animal_type=data["animal_type"],
            feed_stage=data["feed_stage"],
            daily_consumption_kg=data["daily_consumption_kg"],
            bags_needed_per_week=data["bags_needed_per_week"],
            cost_per_week_php=data["cost_per_week_php"],
            reorder_point_days=data["reorder_point_days"],
            alert_level=data["alert_level"],
            weekly_consumption_kg=data["weekly_consumption_kg"],
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        )

        return feed_calculation_log

    def update_feed_calculation_log(self, id: int, payload: UpdateFeedCalculatorPayload) -> Dict:
        payload.updated_at = datetime.now(datetime.timezone.utc)
        response = self.Client.table("feed_calculation_logs") \
            .update(payload) \
            .eq("user_profile_id", id) \
            .execute()

        return response.data[0] if response.data else {}

    def read_growth_performance(self, farmer_user_profile_id: int) -> Dict:
        try:
            user_exists = (self.Client.table("user_profiles")
                           .select("id")
                           .eq("id", farmer_user_profile_id)
                           .limit(1)
                           .execute())

            if not user_exists.data:
                raise GlobalException(
                    f"User profile ID {farmer_user_profile_id} does not exist", 404)

            # Get active feed program
            try:
                feed_program = self.get_active_feed_program(
                    farmer_user_profile_id)
                feed_program_start_date = feed_program.get("start_date")
                feed_program_end_date = feed_program.get("end_date")
                feed_product_id = feed_program.get("feed_product_id")
            except:
                return self.__get_default_growth_performance()

            # get farm performance logs within the active feed program
            farm_performance_logs = []
            if feed_program_start_date:
                query = (
                    self.Client.table("farm_performance_logs")
                    .select("*")
                    .gte("created_at", feed_program_start_date)
                    .order("created_at", desc=True)
                )
                if feed_program_end_date:
                    query = query.lte("created_at", feed_program_end_date)

                farm_logs_response = query.execute()
                farm_performance_logs = farm_logs_response.data or []

            if not farm_performance_logs:
                return self.__get_default_growth_performance()

            total_farm_performance_logs = len(farm_performance_logs)
            latest_farm_performance_log = farm_performance_logs[0]

            # Get the growth rate
            growth_data = self.__calculate_growth_rate(farm_performance_logs)
            growth_rate = growth_data["growth_rate"]

            # get mortality within the feed program period based on dun sa farm performance logs
            total_mortality = sum(log.get("mortality_count", 0)
                                  for log in farm_performance_logs)

            # get farmer flocksize
            flock_size = self.__get_flock_size(farmer_user_profile_id)

            if flock_size > 0:
                mortality_percentage = round(
                    (total_mortality / flock_size) * 100, 2)
                survival_rate = (1 - (total_mortality / flock_size))
            else:
                mortality_percentage = 0.0
                survival_rate = 1.0

            # performance calculation section
            try:
                # average_weight = float(latest_farm_performance_log.get("average_weight_kg", 0.0))
                total_weight_kg = round(
                    sum(float(log.get("average_weight_kg", 0.0)) for log in farm_performance_logs), 3)

                # fcr = float(latest_farm_performance_log.get("feed_convertion_ratio", 1.0))
                # if fcr > 0:
                #     performance_index = round(
                #         ((average_weight * survival_rate) / fcr) * 100, 2)
                # else:
                #     performance_index = 0.0
            except (ValueError, TypeError):
                # average_weight = 0.0
                total_weight_kg = 0.0
                # performance_index = 0.0

            actual_weight = float(
                latest_farm_performance_log.get("average_weight_kg", 0.0))

            # Get target weight based on current feed product
            target_weight = self.__get_target_weight_by_feed_product(
                feed_product_id)

            # Build growth chart data - only for current feed program period
            growth_chart_data = []
            if feed_program_start_date and farm_performance_logs:
                latest_per_day = {}
                for log in farm_performance_logs:
                    date_str = parse(log["created_at"]).date().isoformat()
                    latest_per_day[date_str] = log

                growth_chart_data = [
                    {
                        "date": date,
                        "actual_weight": float(log.get("average_weight_kg", 0.0)),
                        "target_weight": target_weight
                    }
                    for date, log in sorted(latest_per_day.items())
                ]

            # Build recent records - only for current feed program period
            recent_records = []
            if feed_program_start_date and farm_performance_logs:
                program_start_date = parse(feed_program_start_date).date()
                for log in farm_performance_logs:
                    log_date = parse(log["created_at"]).date()
                    day_number = (log_date - program_start_date).days + 1
                    recent_records.append({
                        "date": log_date.isoformat(),
                        "day": f"Day {day_number}",
                        "actual_weight": float(log.get("average_weight_kg", 0.0)),
                        "note": log.get("notes", "")
                    })

            return {
                "daily_average_growth_rate": growth_rate,
                # "current_fcr": float(latest_farm_performance_log.get("feed_conversion_ratio", 0.0)),
                "actual_weight": actual_weight,
                "target_weight": target_weight,
                "growth_chart_data": growth_chart_data,
                "performance_analytics": {
                    "total_logs": total_farm_performance_logs,
                    "total_weight_kg": total_weight_kg,
                    "mortality_count": total_mortality,
                    "mortality_percentage": mortality_percentage,
                    # "performance_index": performance_index,
                    "recent_records": recent_records,
                }
            }

        except GlobalException:
            raise
        except Exception as e:
            raise GlobalException(
                f"Error fetching growth performance: {e}", 500)

    def read_feed_intake_behavior(self, farmer_user_profile_id: int):
        try:
            user_exists = (self.Client.table("user_profiles")
                           .select("id")
                           .eq("id", farmer_user_profile_id)
                           .limit(1)
                           .execute())

            if not user_exists.data:
                raise GlobalException(
                    f"User profile ID {farmer_user_profile_id} does not exist.")

            try:
                feed_program = self.get_active_feed_program(
                    farmer_user_profile_id)
                feed_program_start_date = feed_program.get("start_date")
                feed_program_end_date = feed_program.get("end_date")
                feed_product_id = feed_program.get("feed_product_id")
            except GlobalException:
                return self.__get_default_feed_intake_behavior()

            # get farm performance logs within the active feed program
            farm_performance_logs = []
            if feed_program_start_date:
                query = (
                    self.Client.table("farm_performance_logs")
                    .select("*")
                    .gte("created_at", feed_program_start_date)
                    .order("created_at", desc=True)
                )
                if feed_program_end_date:
                    query = query.lte("created_at", feed_program_end_date)

                farm_logs_response = query.execute()
                farm_performance_logs = farm_logs_response.data or []

            if not farm_performance_logs:
                return self.__get_default_growth_performance()

            # If no logs for this feed program, return defaults
            if not farm_performance_logs:
                return self.__get_default_feed_intake_behavior()

            # Feed intake analysis
            feed_intake_summary = {
                "eating_well": 0,
                "picky": 0,
                "not_eating": 0
            }
            total_feed_behavior_logs = 0

            recent_feed_records = []
            for log in farm_performance_logs:
                behavior = log.get("feed_intake_status")
                if behavior in feed_intake_summary:
                    feed_intake_summary[behavior] += 1
                    total_feed_behavior_logs += 1

                log_date = parse(log["created_at"])
                recent_feed_records.append({
                    "date": log_date.isoformat(),
                    "feed_intake_status": behavior,
                    "feed_intake_kg": log.get("feed_intake_kg")
                })

            # Calculate behavior score
            score_weights = {
                "eating_well": 1.0,
                "picky": 0.5,
                "not_eating": 0.0
            }

            behavior_score = 0.0
            if total_feed_behavior_logs > 0:
                weighted_score = sum(
                    feed_intake_summary[k] * score_weights[k] for k in feed_intake_summary)
                behavior_score = round(
                    (weighted_score / total_feed_behavior_logs) * 100, 2)

            dominant_status = max(
                feed_intake_summary, key=feed_intake_summary.get) if total_feed_behavior_logs > 0 else "no_data"

            return {
                "behavior_score": behavior_score,
                "behavior_status": dominant_status,
                "summary": feed_intake_summary,
                "recent_feed_records": recent_feed_records,
            }

        except GlobalException:
            raise  # Re-raise GlobalException (user not found, etc.)
        except Exception as e:
            raise GlobalException(
                f"Error fetching feed intake behavior: {e}", status_code=500)

    def read_health_watch(self, farmer_user_profile_id: int) -> Dict:
        try:
            user_exists = (self.Client.table("user_profiles")
                           .select("id")
                           .eq("id", farmer_user_profile_id)
                           .limit(1)
                           .execute())

            if not user_exists.data:
                raise GlobalException(
                    f"User profile ID {farmer_user_profile_id} does not exist.", status_code=404)

            try:
                feed_program = self.get_active_feed_program(
                    farmer_user_profile_id)
                feed_program_start_date = feed_program.get("start_date")
                feed_program_end_date = feed_program.get("end_date")
                feed_product_id = feed_program.get("feed_product_id")
            except GlobalException:
                return self.__get_default_feed_intake_behavior()

            # Get health incidents ONLY within the active feed program period
            health_incidents = []
            if feed_program_start_date:
                query = (self.Client.table("health_incidents")
                         .select("*")
                         .gte("created_at", feed_program_start_date)
                         .order("created_at", desc=True))
                if feed_program_end_date:
                    query = query.lte("created_at", feed_program_end_date)
                
                incident_logs_response = query.execute()
                health_incidents = incident_logs_response.data or []

            # If no incidents for this feed program, return defaults
            if not health_incidents:
                return self.__get_default_health_watch()

            sick_count = 0
            mortality_count = 0
            notes_count = 0
            health_score = 100

            recent_issues = []
            for incident in health_incidents:
                kind = incident.get("incident_type")
                affected = incident.get("affected_count", 0)
                has_note = bool(incident.get("symptoms")
                                or incident.get("suspected_cause"))

                if kind == "sickness":
                    sick_count += affected
                    health_score -= affected * 2
                elif kind == "mortality":
                    mortality_count += affected
                    health_score -= affected * 4
                if has_note:
                    notes_count += 1
                    health_score -= 1

                recent_issues.append({
                    "date": incident.get("incident_date"),
                    "incident_type": kind,
                    "affected_count": affected,
                    "symptoms": incident.get("symptoms"),
                    "suspected_cause": incident.get("suspected_cause"),
                    "requires_vet_visit": incident.get("requires_vet_visit"),
                    "feed_info": incident.get("feed_info"),
                    "actions_taken": incident.get("actions_taken"),
                })

            health_score = max(0, min(health_score, 100))

            return {
                "health_score": health_score,
                "issue_summary": {
                    "sick": sick_count,
                    "mortality": mortality_count,
                    "notes": notes_count
                },
                "recent_issues": recent_issues
            }

        except GlobalException:
            raise  # Re-raise GlobalException (user not found, etc.)
        except Exception as e:
            raise GlobalException(
                f"Error fetching health watch data: {e}", status_code=500)

    # HELPER METHODS SECTION -----------------------------------

    def __get_default_growth_performance(self) -> Dict:
        """Return default growth performance structure for new users or users without active feed program"""
        return {
            "daily_average_growth_rate": 0.0,
            "current_fcr": 0.0,
            "actual_weight": 0.0,
            "target_weight": 0.0,
            "growth_chart_data": [],
            "performance_analytics": {
                "total_logs": 0,
                "total_weight_kg": 0.0,
                "mortality_count": 0,
                "mortality_percentage": 0.0,
                "performance_index": 0.0,
                "recent_records": [],
            }
        }

    def __calculate_growth_rate(self, logs: List[Dict]) -> Dict:
        """Calculate growth rate from performance logs"""
        if len(logs) < 2:
            return {
                "growth_rate": 0.0,
                "raw_gain_kg": 0.0
            }

        first_log = logs[-1]  # Oldest log in the period
        last_log = logs[0]    # Most recent log in the period

        try:
            weight_start = float(first_log.get("average_weight_kg", 0.0))
            weight_end = float(last_log.get("average_weight_kg", 0.0))
            date_start = parse(first_log["created_at"])
            date_end = parse(last_log["created_at"])

            days = (date_end - date_start).days
            if days <= 0:
                return {
                    "growth_rate": 0.0,
                    "raw_gain_kg": 0.0
                }

            return {
                "growth_rate": round((weight_end - weight_start) / days, 3),
                "raw_gain_kg": round((weight_end - weight_start), 3)
            }
        except (ValueError, TypeError) as e:
            print(f"Error calculating growth rate: {e}")
            return {
                "growth_rate": 0.0,
                "raw_gain_kg": 0.0
            }

    def __get_default_feed_intake_behavior(self) -> Dict:
        """Return default feed intake behavior structure for new users or users without active feed program"""
        return {
            "behavior_score": 0.0,
            "behavior_status": "no_data",
            "summary": {
                "eating_well": 0,
                "picky": 0,
                "not_eating": 0
            },
            "recent_feed_records": [],
        }

    def __get_default_health_watch(self) -> Dict:
        """Return default health watch structure for new users or users without active feed program"""
        return {
            "health_score": 100,
            "issue_summary": {
                "sick": 0,
                "mortality": 0,
                "notes": 0
            },
            "recent_issues": []
        }

    def __get_flock_size(self, farmer_user_profile_id: int) -> int:
        """Get flock size for the farmer"""
        try:
            # Get flock size
            flock_size_response = self.Client.table("farmer_livestock").select("quantity") \
                .eq("farmer_user_profile_id", farmer_user_profile_id).single().execute()

            if flock_size_response.data:
                return flock_size_response.data.get("quantity", 0)
        except Exception:
            pass

        return 0

    def __get_target_weight_by_feed_product(self, feed_product_id: Optional[int]) -> float:
        """Get target weight based on feed product ID"""
        if not feed_product_id:
            return 0.0

        try:
            target_weight_response = self.Client.table("feed_growth_targets").select("target_weight_kg") \
                .eq("feed_product_id", feed_product_id).limit(1).single().execute()

            if target_weight_response.data:
                return float(target_weight_response.data["target_weight_kg"])
        except Exception:
            pass

        return 0.0
