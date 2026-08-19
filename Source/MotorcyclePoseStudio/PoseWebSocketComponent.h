#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "IWebSocket.h"
#include "Delegates/DelegateCombinations.h"
#include "PoseWebSocketComponent.generated.h"

USTRUCT(BlueprintType)
struct FRiderState
{
    GENERATED_BODY()
   
    float HeadYawRatio = 0.0f;
	float HeadRoll = 0.0f;
    float LeftElbow = 0.0f;
    float RightElbow = 0.0f;
    float LeftKnee = 0.0f;
    float RightKnee = 0.0f;
    float LeftFoot = 0.0f;
    float RightFoot = 0.0f;
    float TorsoAngle = 0.0f;
    float PoseConfidence = 0.0f;
    bool bClutchInFrictionZone = false;
    float ClutchProgress = 0.0f;
    bool bHasClutchProgress = false;
    float FrontBrakeProgress = 0.0f;
    bool bHasFrontBrakeProgress = false;
    bool bFrontBrakeActive = false;
    float ThrottleProgress = 0.0f;
    bool bHasThrottleProgress = false;
    bool bThrottleActive = false;
    UPROPERTY(BlueprintReadOnly)
    float RearBrakeProgress = 0.0f;
    bool bHasRearBrakeProgress = false;
    UPROPERTY(BlueprintReadOnly)
    bool bRearBrakeActive = false;
    
   
    
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE(
    FRearBrakeAppliedSignature
);

DECLARE_DYNAMIC_MULTICAST_DELEGATE(
    FRearBrakeReleasedSignature
);

DECLARE_DYNAMIC_MULTICAST_DELEGATE(
    FThrottleOpenedSignature
);

DECLARE_DYNAMIC_MULTICAST_DELEGATE(
    FThrottleClosedSignature
);

DECLARE_DYNAMIC_MULTICAST_DELEGATE(
    FFrontBrakeAppliedSignature
);

DECLARE_DYNAMIC_MULTICAST_DELEGATE(
    FFrontBrakeReleasedSignature
);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(
    FClutchFrictionZoneEnteredSignature
);

DECLARE_DYNAMIC_MULTICAST_DELEGATE(
    FClutchFrictionZoneExitedSignature
);
UCLASS(ClassGroup = (Custom), meta = (BlueprintSpawnableComponent))
class MOTORCYCLEPOSESTUDIO_API UPoseWebSocketComponent : public UActorComponent
{
    GENERATED_BODY()

private:
    bool bPreviousFrontBrakeActive = false;
    bool bHasPreviousFrontBrakeState = false;
    bool bPreviousThrottleActive = false;
    bool bHasPreviousThrottleState = false;
    bool bPreviousClutchInFrictionZone = false;
    bool bHasPreviousClutchState = false;
    bool bPreviousRearBrakeActive = false;
    bool bHasPreviousRearBrakeState = false;

public:
    UPoseWebSocketComponent();
    UPROPERTY(
        BlueprintAssignable,
        Category = "Pose|Controls"
    )
    FClutchFrictionZoneEnteredSignature
        OnClutchFrictionZoneEntered;

    UPROPERTY(
        BlueprintAssignable,
        Category = "Pose|Controls"
    )
    FClutchFrictionZoneExitedSignature
        OnClutchFrictionZoneExited;

    UPROPERTY(
        BlueprintAssignable,
        Category = "Pose|Controls"
    )
    FThrottleOpenedSignature OnThrottleOpened;

    UPROPERTY(
        BlueprintAssignable,
        Category = "Pose|Controls"
    )
    FThrottleClosedSignature OnThrottleClosed;

    UPROPERTY(BlueprintReadOnly, Category = "Pose|Controls")
    bool bFrontBrakeActive = false;
    UPROPERTY(
        BlueprintAssignable,
        Category = "Pose|Controls"
    )
    FFrontBrakeAppliedSignature OnFrontBrakeApplied;

    UPROPERTY(
        BlueprintAssignable,
        Category = "Pose|Controls"
    )
    FFrontBrakeReleasedSignature OnFrontBrakeReleased;

    UPROPERTY(
        BlueprintAssignable,
        Category = "Pose|Controls"
    )
    FRearBrakeAppliedSignature OnRearBrakeApplied;

    UPROPERTY(
        BlueprintAssignable,
        Category = "Pose|Controls"
    )
    FRearBrakeReleasedSignature OnRearBrakeReleased;

protected:
    virtual void BeginPlay() override;

public:
    virtual void TickComponent(
        float DeltaTime,
        ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction
    ) override;

private:
    TSharedPtr<IWebSocket> WebSocket;
   
    void Connect();

    void HandleConnected();
    void HandleConnectionError(const FString& Error);
    void HandleClosed(
        int32 StatusCode,
        const FString& Reason,
        bool bWasClean
    );
    void HandleMessage(const FString& Message);
    bool ParseRiderState(
        const FString& Message,
        FRiderState& OutRiderState
    ) const; 
    
};